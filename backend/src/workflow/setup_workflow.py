from langgraph.graph import StateGraph, END
from .state import ResearchState
from .nodes import (
    init_search,
    google_search_node,
    bing_search_node,
    reddit_search_node,
    yahoo_finance_node,
    research_analyst_node,
    report_writing_node,
)

def create_workflow():
    """
    Creates the research workflow graph.

    Returns:
        The compiled workflow graph.
    """
    workflow = StateGraph(ResearchState)

    # Add nodes
    workflow.add_node("init_search", init_search)
    workflow.add_node("google_search", google_search_node)
    workflow.add_node("bing_search", bing_search_node)
    workflow.add_node("reddit_search", reddit_search_node)
    workflow.add_node("yahoo_finance", yahoo_finance_node)
    workflow.add_node("research_analyst", research_analyst_node)
    workflow.add_node("report_writer", report_writing_node)

    # Set entry point
    workflow.set_entry_point("init_search")

    # Add edges
    workflow.add_edge("init_search", "google_search")
    workflow.add_edge("google_search", "bing_search")
    workflow.add_edge("bing_search", "reddit_search")
    workflow.add_edge("reddit_search", "yahoo_finance")
    workflow.add_edge("yahoo_finance", "research_analyst")
    workflow.add_edge("research_analyst", "report_writer")
    workflow.add_edge("report_writer", END)

    # Compile the graph
    graph = workflow.compile()
    return graph
