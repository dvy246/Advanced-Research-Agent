from typing import Any
import asyncpraw
import asyncio
import os
from aiocache.backends.redis import RedisCache
from aiocache import caches,cached

# Load Reddit API credentials from environment variables (with default fallback)
client_id = os.getenv('REDDIT_CLIENT_ID')
client_secret = os.getenv('REDDIT_CLIENT_SECRET')
user_agent = 'dp by /u/Temporary_Version105'

caches.set_config({
    'default': {
        'cache': 'aiocache.backends.redis.RedisCache', 
        'endpoint': '127.0.0.1',                       
        'port': 6379,                               
        'serializer': {'class': 'aiocache.serializers.PickleSerializer'},
        'ttl': 4800 
    }})

@cached(alias='default', 
        key_builder=lambda f, post: f'post_data:{post.id}', 
        fail_safe=True)
async def fetch_posts(post):
    """
    This function will automatically check the cache first.
    If there is a MISS, the code below runs (slow part).
    If there is a HIT, the decorator returns the cached result instantly.
    """
    print(f"--- Cache MISS: Loading post and comments for {post.id}")
    
    # --- Your existing complex comment fetching and data structuring logic goes here ---
    try:
        await post.load()
        await post.comments.replace_more()

        comments=[]

        for com in post.comments.list()[:50]:
            if hasattr(com,'body')  and com.body.strip():
                   comments.append(
                            {
                                "id": com.id,
                                "body": com.body,
                                "author": str(getattr(com, "author", "N/A")),
                                "score": getattr(com, "score", 0),
                                "depth": com.depth,   
                                "controversiality": com.controversiality,
                                "gilded": com.gilded,
                                "total_awards_received": com.total_awards_received,
                            }
                        )
        return { 
            "title": getattr(post, "title", "N/A"),
            "score": getattr(post, "score", 0),
            "comments": comments # The list of processed comments
        }
    except Exception as e:
        print(f"Error loading post {post.id}: {e}")
        return None # Do not cache failures


async def fetch_reddit_posts():
    """
    Fetch 'hot' posts and top-level comments from r/finance and store in cache.
    Skips posts if already cached. Stores post IDs for easy querying later.
    """
    cache = caches.get('default')
    print("Connecting to Reddit...")
    
    reddit = asyncpraw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )
    try:
        # Get the finance subreddit
        subreddit = await reddit.subreddit('finance')
        post_processed = 0

        #storing post ids in the list 
        post_ids = []
        # Iterate over hot posts (limit 10 for demo)
        async for post in subreddit.hot(limit=50):
            post_processed += 1
            post_id = post.id
            post_ids.append(post_id)

            #post cache key
            post_cache_key = f'post:{post_id}'
            
            # Check if this post is already cached
            cached_post = await cache.get(post_cache_key)
            if cached_post:
                print(f"  > Using cached: {cached_post.get('title', 'No Title')[:100]}")
                continue

            # Fetch data if not cached
            else:
                try:
                    # Fully load post and expand all comments (no 'more')
                  post_data=await fetch_posts(post)
                  if post_data:
                    post_ids.append(post.id)

                except asyncio.TimeoutError:
                    print(f"  > Timeout fetching post: {post.title[:100]}")
        # After the loop, store the list of post IDs from this run.
        await cache.set('all_post_ids', post_ids, ttl=4800)
        print(f'Session post ids set with length {len(post_ids)}')

    except asyncio.TimeoutError:
        print("Operation timed out.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Always close Reddit API connection
        await reddit.close()  

async def get_posts(post_id):
    cache = caches.get('default')
    cache_key = f"post:{post_id}"

    cached_post = await cache.get(cache_key)
    if cached_post:
        print(f"--- Cache HIT: {post_id}")
        return cached_post

    print(f"--- Cache MISS: Loading post and comments for {post_id}")

    reddit = asyncpraw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent
    )

    try:
        submission = await reddit.submission(id=post_id)
        post_data = await fetch_posts(submission)

        await cache.set(cache_key, post_data, ttl=4800)

        return post_data

    except Exception as e:
        print(f"Error getting posts for postid {post_id}: {e}")
        return None

    finally:
        await reddit.close()


async def get_all_comments():
    """
    Retrieve all cached comments from all posts currently stored in cache.
    Returns a flat list of comments (good for analysis or language models).
    """
    cache = caches.get('default')
    
    # Find all cached post IDs
    post_ids = await cache.get('all_post_ids') or []
    
    if not post_ids:
        print("⚠️  No cached posts found. Run fetch_reddit_posts() first!")
        return []
    
    all_comments = []
    print(f"📥 Collecting comments from {len(post_ids)} posts...\n")
    
    # Gather all comments for each post (add post_id for provenance)
    for post_id in post_ids:
        post_data = await get_posts(post_id)
        if post_data and 'comments' in post_data:
            for comment in post_data['comments']:
                comment['post_id'] = post_id  
                all_comments.append(comment)
    
    print(f"✅ Total comments collected: {len(all_comments)}")
    return all_comments

async def main():
    result1,result2=await asyncio.gather(fetch_reddit_posts(), get_all_comments())
    print(result1)
    print(result2)

if __name__ == "__main__":
    import os

    if (
        os.environ.get("REDDIT_CLIENT_ID") and
        os.environ.get("REDDIT_CLIENT_SECRET") and
        os.environ.get("REDDIT_USER_AGENT")
    ):
        asyncio.run(main())
    else:
        print("❌ Reddit API credentials are missing! Please set the following environment variables:")
        print("   REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT")
        print("You can do this in your shell before running the script, e.g.:")
        print("export REDDIT_CLIENT_ID='your_id'")
        print("export REDDIT_CLIENT_SECRET='your_secret'")
        print("export REDDIT_USER_AGENT='your_agent_name'")