from typing import TypedDict, List, Optional

class ResearchState(TypedDict):
    """
    Represents the state of the research workflow.

    Attributes:
        query (str): The initial research query.
        report (str): The final research report.
        search_results (List[dict]): A list of search results from various sources.
        analysis (Optional[str]): The analysis of the search results.
    """
    query: str
    report: str
    search_results: List[dict]
    analysis: Optional[str]
