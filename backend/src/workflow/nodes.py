from ..tools.google.google_search import google_search
from ..tools.search_sys.bing import bing
from ..tools.google.google_finance import google_finance
from ..tools.search_sys.yfinance  import main
from .state import ResearchState
from ..config.model import Model
from ..config.str_outputs import QueryClassifier
from ..tools.reddit_comments import reddit
import asyncio
from ..config.setup_logs import logger


llm=Model().set_model()


async def init_search(state: ResearchState):
    logger.info("---INITIATING RESEARCH---")
    user_question = state.get("user_question")
    if user_question is None:
        raise ValueError("User question not found in the state.")
    return {"user_question": user_question}

async def classify_question_node(state: ResearchState):
    """
    Classifies the user's question as either 'finance' or 'general'.
    """
    logger.info("---CLASSIFYING USER QUESTION---")
    user_question = state["user_question"]

    if not user_question:
        raise ValueError("User question not found in the state.")
    
    prompt = f"""
    You are an advanced language model specializing in categorizing user queries for a multi-domain research assistant platform.

    Your task: Carefully analyze the provided user query and classify it into one of the following predefined categories:
      1. 'finance': The query is primarily about financial matters such as stock prices, company financials, economic indicators, investment strategies, market trends, or financial news if the question mentions anything about the company  is a finance.
      2. 'general': The query covers any topic unrelated to finance, such as science, history, technology, entertainment, or other general knowledge domains.
      3. 'finance and general': The query contains both financial and non-financial (general) aspects within a single sentence or topic.

    Guidelines:
      - Base your classification solely on the query's content and intent.
      - Consider nuances in language that may combine financial and general interests.
      - Your answer must be a single label (exactly 'finance', 'general', or 'finance and general') with no additional commentary.
      - This classification will be used by an automated workflow to determine subsequent research steps and agent routing, so accuracy and precision are vital.

    User Query: "{user_question}"
    """
    
    try:
        # Create a structured output LLM
        structured_llm = llm.with_structured_output(QueryClassifier)
        
        # Invoke the LLM
        classification_result = await structured_llm.ainvoke(prompt)
        
        logger.info(f"Query classified as: {classification_result.query_type}")
        
        # Update the state
        return {"query_type": classification_result.query_type}
        
    except Exception as e:
        logger.error(f"Error during classification: {e}")

async def google_search_node(state: ResearchState):
    """
    Performs a Google search and updates the state with the results.
    """
    logger.info("---PERFORMING GOOGLE SEARCH---")
    query = state["user_question"]
    google_results = await google_search(query)
    return {"google_search_results": google_results}


async def bing_search_node(state: ResearchState):
    """
    Performs a Bing search and updates the state with the results.
    """
    logger.info("---PERFORMING BING SEARCH---")
    query = state["user_question"]
    bing_results = await bing(query)
    return {"bing_search_results": bing_results}

async def reddit_search_node(state: ResearchState):
    """
    Performs a Reddit search and updates the state with the results.
    """
    logger.info("---PERFORMING REDDIT SEARCH---")
    reddit_results = await reddit() # Get all comments from cache
    return {"reddit_search_results": reddit_results}

async def yahoo_finance_node(state: ResearchState):
    """
    Performs a Yahoo Finance search (using google_finance tool) and updates the state with the results.
    """
    logger.info("---PERFORMING YAHOO FINANCE SEARCH---")
    query = state["user_question"]
    yahoo_results = await main(query)
    return {"yahoo_finance_results": yahoo_results}

async def google_search_node(state:ResearchState):
    """
    performs search using google finance tool
    """
    logger.info("---PERFORMING GOOGLE SEARCH---")
    query = state["user_question"]
    google_results = await google_search(query)
    return {"google_search_results": google_results}

async def google_search_analysis_node(state: ResearchState):
    logger.info("---ANALYZING GOOGLE SEARCH RESULTS---")
    user_question = state["user_question"]
    google_results = state["google_search_results"]
    prompt = f"""Analyze the following Google search results for the query: {user_question}

    Search Results:
    {google_results}

    Provide a detailed analysis of the Google search results.
    """
    analysis = await llm.ainvoke(prompt)
    return {"google_analysis": analysis.content}

async def bing_search_analysis_node(state: ResearchState):
    logger.info("---ANALYZING BING SEARCH RESULTS---")
    user_question = state["user_question"]
    bing_results = state["bing_search_results"]
    prompt = f"""Analyze the following Bing search results for the query: {user_question}

    Search Results:
    {bing_results}

    Provide a detailed analysis of the Bing search results.
    """
    analysis = await llm.ainvoke(prompt)
    return {"bing_analysis": analysis.content}

async def reddit_comments_analysis_node(state: ResearchState):
    logger.info("---ANALYZING REDDIT COMMENTS---")
    user_question = state["user_question"]
    reddit_results = state["reddit_search_results"]
    prompt = f"""Analyze the following Reddit comments for the query: {user_question}

    Reddit Comments:
    {reddit_results}

    Provide a detailed analysis of the Reddit comments, focusing on sentiment, key topics, and common opinions.
    """
    analysis = await llm.ainvoke(prompt)
    return {"reddit_analysis": analysis.content}

async def yahoo_finance_analysis_node(state: ResearchState):
    logger.info("---ANALYZING YAHOO FINANCE DATA---")
    user_question = state["user_question"]
    finance_results = state["yahoo_finance_results"]
    prompt = f"""Analyze the following Yahoo Finance data for the query: {user_question}

    Yahoo Finance Data:
    {finance_results}

    Provide a detailed analysis of the financial data, focusing on key metrics, trends, and potential implications.
    """
    analysis = await llm.ainvoke(prompt)
    return {"yahoo_finance_analysis": analysis.content}

async def google_finance_analysis_node(state: ResearchState):
    logger.info("---ANALYZING GOOGLE FINANCE DATA---")
    user_question = state["user_question"]
    finance_results = state["google_finance_results"]
    prompt = f"""Analyze the following Google Finance data for the query: {user_question}

    Google Finance Data:
    {finance_results}

    Provide a detailed analysis of the financial data, focusing on key metrics, trends, and potential implications.
    """
    analysis = await llm.ainvoke(prompt)
    return {"google_finance_analysis": analysis.content}

async def aggregate_analysis_node_first(state: ResearchState):
    logger.info("---AGGREGATING ALL ANALYSES---")
    user_question = state["user_question"]
    yahoo_finance_analysis = state.get("yahoo_finance_analysis", "")
    google_finance_analysis = state.get("google_finance_analysis", "")

    combined_analysis = f"""
    User Question: {user_question}
    
    ur a finance expert so u will get 2 analysis one of yahoo and google so ur job is to make 
    a report based on both and provide a combined report for the same which is based on data facts and non hallucinations
    Yahoo Finance Analysis:
    {yahoo_finance_analysis}

    Google Finance Analysis:
    {google_finance_analysis}
    """
    
    first_combined_search=await llm.ainvoke(input=combined_analysis)
    return {"combined_analysis_1": first_combined_search}

async def aggregate_analysis_node_second(state: ResearchState):
    logger.info("---AGGREGATING ALL ANALYSES---")
    bing_analysis = state.get("bing_analysis", "")
    reddit_analysis = state.get("reddit_analysis", "")
    combined_analysis = f"""

    Bing Search Analysis:
    {bing_analysis}

    Reddit Comments Analysis:
    {reddit_analysis}
    """

    second_combined_search=await llm.ainvoke(input=combined_analysis)
    return {"combined_analysis_2": second_combined_search}

async def synthesize_report_node(state: ResearchState):
    logger.info("---SYNTHESIZING REPORT---")
    user_question = state["user_question"]
    
    # Get the two separate analyses from the state
    analysis_1 = state.get("combined_analysis_1", "")
    analysis_2 = state.get("combined_analysis_2", "")

    prompt = f"""Based on the following combined analysis for the query: {user_question}, synthesize a comprehensive report.

    Combined Financial Analysis:
    {analysis_1}

    Combined Web/Social Analysis:
    {analysis_2}

    The report should be well-structured, insightful, and address the user's question thoroughly.
    """
    synthesized_report = await llm.ainvoke(prompt)
    return {"synthesized_answer": synthesized_report.content}

async def synthesized_report_analysis_node(state: ResearchState):
    logger.info("---ANALYZING SYNTHESIZED REPORT---")
    user_question = state["user_question"]
    synthesized_answer = state["synthesized_answer"]
    prompt = f"""Analyze the following synthesized report for the query: {user_question}.

    Synthesized Report:
    {synthesized_answer}

    Provide a critical analysis of the report, highlighting its strengths, weaknesses, and any areas that could be improved or further investigated.
    """
    analysis = await llm.ainvoke(prompt)
    return {"report": analysis.content} 

async def major_highlights_node(state: ResearchState):
    logger.info("---EXTRACTING MAJOR HIGHLIGHTS---")
    synthesized_answer = state["synthesized_answer"]
    prompt = f"""From the following synthesized report, extract the major highlights and key takeaways.

    Synthesized Report:
    {synthesized_answer}

    Provide a concise list of the most important points.
    """
    highlights = await llm.ainvoke(prompt)
    return {"major_highlights": highlights.content}

async def final_report_node(state: ResearchState):
    logger.info("---GENERATING FINAL REPORT---")
    user_question = state["user_question"]
    synthesized_answer = state["synthesized_answer"]
    report_analysis = state.get("report", "") 
    major_highlights = state.get("major_highlights", "")

    final_report_content = f"""
    # Research Report for: {user_question}

    ## Synthesized Answer:
    {synthesized_answer}

    ## Major Highlights:
    {major_highlights}

    ## Report Analysis:
    {report_analysis}

    ---
    This report was generated by an AI research agent.
    """
    return {"final_report": final_report_content}
