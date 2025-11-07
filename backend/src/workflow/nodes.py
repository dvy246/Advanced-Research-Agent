
from ..tools.google.google_search import google_search
from ..tools.search_sys.bing import bing
from ..tools.reddit_comments import fetch_reddit_posts
from ..tools.google.google_finance import google_finance
from .state import ResearchState
from ..config.model import Model
import asyncio

async def init_search(state: ResearchState):
    """
    Initializes the search process by taking the user's query.
    
    Args:
        state (ResearchState): The current state of the workflow.
        
    Returns:
        ResearchState: The updated state with the query.
    """
    print("---INITIATING RESEARCH---")
    query = state.get("query")
    if query is None:
        raise ValueError("Query not found in the state.")
    return {"query": query}

async def google_search_node(state: ResearchState):
    """
    Performs a Google search and updates the state with the results.
    
    Args:
        state (ResearchState): The current state of the workflow.
        
    Returns:
        ResearchState: The updated state with Google search results.
    """
    print("---PERFORMING GOOGLE SEARCH---")
    query = state["query"]
    loop = asyncio.get_event_loop()
    google_results = await loop.run_in_executor(None, asyncio.run, google_search(query))
    return {"search_results": google_results}

async def bing_search_node(state: ResearchState):
    """
    Performs a Bing search and updates the state with the results.
    
    Args:
        state (ResearchState): The current state of the workflow.
        
    Returns:
        ResearchState: The updated state with Bing search results.
    """
    print("---PERFORMING BING SEARCH---")
    query = state["query"]
    loop = asyncio.get_event_loop()
    bing_results = await loop.run_in_executor(None, asyncio.run, bing(query))
    # Append results to existing search_results
    current_results = state.get("search_results", [])
    current_results.extend(bing_results)
    return {"search_results": current_results}

async def reddit_search_node(state: ResearchState):
    """
    Performs a Reddit search and updates the state with the results.
    
    Args:
        state (ResearchState): The current state of the workflow.
        
    Returns:
        ResearchState: The updated state with Reddit search results.
    """
    print("---PERFORMING REDDIT SEARCH---")
    loop = asyncio.get_event_loop()
    reddit_results = await loop.run_in_executor(None, asyncio.run, fetch_reddit_posts())
    current_results = state.get("search_results", [])
    current_results.extend(reddit_results)
    return {"search_results": current_results}

async def yahoo_finance_node(state: ResearchState):
    """
    Performs a Yahoo Finance search and updates the state with the results.
    
    Args:
        state (ResearchState): The current state of the workflow.
        
    Returns:
        ResearchState: The updated state with Yahoo Finance search results.
    """
    print("---PERFORMING YAHOO FINANCE SEARCH---")
    query = state["query"]
    loop = asyncio.get_event_loop()
    yahoo_results = await loop.run_in_executor(None, asyncio.run, google_finance(query))
    current_results = state.get("search_results", [])
    current_results.extend(yahoo_results)
    return {"search_results": current_results}

async def research_analyst_node(state: ResearchState):
    """
    Analyzes the search results and generates an analysis.
    
    Args:
        state (ResearchState): The current state of the workflow.
        
    Returns:
        ResearchState: The updated state with the analysis.
    """
    print("---ANALYZING SEARCH RESULTS---")
    query = state["query"]
    search_results = state["search_results"]
    
    model = Model()
    llm = model.set_model()
    
    prompt = f"""Analyze the following search results for the query: {query}

    Search Results:
    {search_results}

    Provide a detailed analysis of the search results.
    """
    
    loop = asyncio.get_event_loop()
    analysis = await loop.run_in_executor(None, asyncio.run, llm.ainvoke(prompt))
    
    return {"analysis": analysis.content}

async def report_writing_node(state: ResearchState):
    """
    Writes a report based on the analysis.
    
    Args:
        state (ResearchState): The current state of the workflow.
        
    Returns:
        ResearchState: The updated state with the report.
    """
    print("---WRITING REPORT---")
    analysis = state["analysis"]
    
    model = Model()
    llm = model.set_model()
    
    prompt = f"""Based on the following analysis, write a detailed report.

    Analysis:
    {analysis}

    The report should be well-structured and easy to read.
    """
    
    loop = asyncio.get_event_loop()
    report = await loop.run_in_executor(None, asyncio.run, llm.ainvoke(prompt))
    
    return {"report": report.content}
