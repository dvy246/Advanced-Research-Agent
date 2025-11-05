import asyncio
import os
import types
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

# Target module
import src.tools.reddit_comments as rc


@pytest.mark.asyncio
async def test_fetch_posts_cache_miss_builds_comment_list_and_returns_structure():
    # Create a fake comment object with required attributes
    def make_comment(idx, depth=0):
        c = types.SimpleNamespace()
        c.id = f"c{idx}"
        c.body = f"body {idx}"
        c.author = f"author{idx}"
        c.score = idx
        c.depth = depth
        c.controversiality = 0
        c.gilded = 0
        c.total_awards_received = 0
        return c

    # Fake post with needed async methods/attributes
    post = types.SimpleNamespace()
    post.id = "post123"
    post.title = "A Title"
    post.score = 42
    post.load = AsyncMock()
    # comments replacement and listing
    comments_mgr = types.SimpleNamespace()
    comments_mgr.replace_more = AsyncMock()
    comments_mgr.list = MagicMock(return_value=[make_comment(i) for i in range(5)])
    post.comments = comments_mgr

    # The cached decorator will attempt cache; ensure it doesn't explode by isolating cache backends
    result = await rc.fetch_posts(post)

    assert result["title"] == "A Title"
    assert result["score"] == 42
    assert isinstance(result["comments"], list)
    assert len(result["comments"]) == 5
    assert {"id", "body", "author", "score", "depth", "controversiality", "gilded", "total_awards_received"} <= set(result["comments"][0].keys())


@pytest.mark.asyncio
async def test_get_posts_hits_cache_and_returns_cached_value():
    fake_cached = {"title": "cached", "score": 1, "comments": []}

    with patch.object(rc.caches, 'get') as get_cache:
        cache = MagicMock()
        cache.get = AsyncMock(return_value=fake_cached)
        get_cache.return_value = cache

        res = await rc.get_posts("abc")

        assert res is fake_cached
        cache.get.assert_awaited_once_with("post:abc")


@pytest.mark.asyncio
async def test_get_posts_miss_fetches_via_asyncpraw_and_sets_cache():
    with patch.object(rc.caches, 'get') as get_cache, \
         patch('src.tools.reddit_comments.asyncpraw.Reddit') as Reddit:
        cache = MagicMock()
        cache.get = AsyncMock(return_value=None)
        cache.set = AsyncMock()
        get_cache.return_value = cache

        # Mock Reddit and submission
        reddit = MagicMock()
        Reddit.return_value = reddit
        submission = types.SimpleNamespace(id="abc")
        reddit.submission = AsyncMock(return_value=submission)
        reddit.close = AsyncMock()

        # Spy on fetch_posts to avoid exercising its internals again
        fetched = {"title": "t", "score": 0, "comments": []}
        with patch('src.tools.reddit_comments.fetch_posts', new=AsyncMock(return_value=fetched)) as fp:
            res = await rc.get_posts("abc")

        assert res == fetched
        reddit.submission.assert_awaited_once_with(id="abc")
        cache.set.assert_awaited_once_with("post:abc", fetched, ttl=4800)
        reddit.close.assert_awaited()


@pytest.mark.asyncio
async def test_get_all_comments_no_post_ids_returns_empty_list_and_no_errors():
    with patch.object(rc.caches, 'get') as get_cache:
        cache = MagicMock()
        cache.get = AsyncMock(return_value=None)
        get_cache.return_value = cache

        res = await rc.get_all_comments()
        assert res == []


@pytest.mark.asyncio
async def test_get_all_comments_collects_from_multiple_posts():
    with patch.object(rc.caches, 'get') as get_cache:
        cache = MagicMock()
        cache.get = AsyncMock(side_effect=[["p1", "p2"], {"title": "t1", "comments": [{"id": "c1"}]}, {"title": "t2", "comments": [{"id": "c2"}, {"id": "c3"}]}])
        get_cache.return_value = cache

        # Patch get_posts to return controlled data corresponding to post ids
        async def fake_get_posts(pid):
            if pid == "p1":
                return {"title": "t1", "comments": [{"id": "c1"}]}
            if pid == "p2":
                return {"title": "t2", "comments": [{"id": "c2"}, {"id": "c3"}]}
            return None

        with patch('src.tools.reddit_comments.get_posts', new=fake_get_posts):
            res = await rc.get_all_comments()

        # Should annotate with post_id
        assert len(res) == 3
        assert {c['id'] for c in res} == {"c1", "c2", "c3"}
        assert {c['post_id'] for c in res} == {"p1", "p2"}
