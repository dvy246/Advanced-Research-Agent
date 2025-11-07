from typing import TypedDict, List, Optional, Annotated
from langgraph.graph.message import add_messages

class ResearchState(TypedDict):
    """
    Represents the state of the research workflow.
    """
    messages: Annotated[list, add_messages]
    user_question: str
    google_search_results: Optional[str]
    google_finance_results: Optional[str]
    bing_search_results: Optional[str]
    reddit_search_results: Optional[str]
    selected_reddit_urls: Optional[List[str]]
    reddit_posts: Optional[str]
    google_analysis: Optional[str]
    bing_analysis: Optional[str]
    reddit_analysis: Optional[str]
    google_finance_analysis: Optional[str]
    synthesized_answer: Optional[str]
    report: Optional[str]
    major_highlights: Optional[str]
    final_report: Optional[str]
