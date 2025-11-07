# backend/src/workflow/setup_workflow.py

from langgraph.graph import StateGraph, END
from .state import ResearchState
from .nodes import (
    init_search,
    classify_question_node, 
    google_search_node,
    bing_search_node,
    reddit_search_node,
    yahoo_finance_node,
    google_finance_search,     
    google_search_analysis_node,
    bing_search_analysis_node,
    reddit_comments_analysis_node,
    yahoo_finance_analysis_node,
    google_finance_analysis_node,
    aggregate_analysis_node_first,
    aggregate_analysis_node_second,
    synthesize_report_node,
    synthesized_report_analysis_node,
    major_highlights_node,
    final_report_node,
    router
)

def create_workflow():
    """
    Creates the research workflow graph with conditional routing.
    """
    workflow = StateGraph(ResearchState)

    # --- 1. Add ALL nodes to the graph ---
    workflow.add_node("init_search", init_search)
    workflow.add_node("classify_question", classify_question_node)
    
    # General Search Branch
    workflow.add_node("google_search", google_search_node)
    workflow.add_node("bing_search", bing_search_node)
    workflow.add_node("google_search_analysis", google_search_analysis_node)
    workflow.add_node("bing_search_analysis", bing_search_analysis_node)
    workflow.add_node("aggregate_general_analysis_2", aggregate_analysis_node_second)

    # Finance Search Branch
    workflow.add_node("google_finance_search", google_finance_search)
    workflow.add_node("yahoo_finance_search", yahoo_finance_node)
    workflow.add_node("reddit_search", reddit_search_node)
    workflow.add_node("google_finance_analysis", google_finance_analysis_node)
    workflow.add_node("yahoo_finance_analysis", yahoo_finance_analysis_node)
    workflow.add_node("reddit_analysis", reddit_comments_analysis_node)
    workflow.add_node("aggregate_finance_analysis_1", aggregate_analysis_node_first)

    # Final Reporting Branch
    workflow.add_node("synthesize_report", synthesize_report_node)
    workflow.add_node("analyze_synthesized_report", synthesized_report_analysis_node)
    workflow.add_node("extract_highlights", major_highlights_node)
    workflow.add_node("generate_final_report", final_report_node)

    # --- 2. Define the graph flow ---
    
    # Entry point
    workflow.set_entry_point("init_search")
    
    # Run classifier right after init
    workflow.add_edge("init_search", "classify_question")

    workflow.add_conditional_edges("classify_question", router)

    # --- 4. Define the "Finance" branch flow ---
    workflow.add_edge("google_finance_search", "google_finance_analysis")
    workflow.add_edge("yahoo_finance_search", "yahoo_finance_analysis")
    workflow.add_edge("reddit_search", "reddit_analysis")
    
    # Join all finance analyses at the first aggregator
    workflow.add_edge("google_finance_analysis", "aggregate_finance_analysis_1")
    workflow.add_edge("yahoo_finance_analysis", "aggregate_finance_analysis_1")
    workflow.add_edge("reddit_analysis", "aggregate_finance_analysis")

    # --- 5. Define the "General" branch flow ---
    workflow.add_edge("google_search", "google_search_analysis")
    workflow.add_edge("bing_search", "bing_search_analysis")
    
    # Join all general analyses at the second aggregator
    workflow.add_edge("google_search_analysis", "aggregate_general_analysis_2")
    workflow.add_edge("bing_search_analysis", "aggregate_general_analysis_2")

    # --- 6. Join both branches back together for synthesis ---
    workflow.add_edge("aggregate_finance_analysis", "synthesize_report")
    workflow.add_edge("aggregate_general_analysis", "synthesize_report")

    # --- 7. Define the final reporting flow ---
    # Run highlight extraction and report analysis in parallel
    workflow.add_edge("synthesize_report", "analyze_synthesized_report")
    workflow.add_edge("synthesize_report", "extract_highlights")
    
    # Join them for the final report generation
    workflow.add_edge("analyze_synthesized_report", "generate_final_report")
    workflow.add_edge("extract_highlights", "generate_final_report")
    
    # End the graph
    workflow.add_edge("generate_final_report", END)

    # Compile the graph
    graph = workflow.compile()
    return graph

create_workflow()