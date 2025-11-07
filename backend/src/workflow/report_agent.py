from langchain.agents import create_agent
from src.config.model import model
from src.config.setup_logs import logger
from src.config import yaml_load
import asyncio
from src.config.str_outputs import Report

llm=model.set_model()

prompt=yaml_load('report_making_agent')

async def reporting_agent(content:str):
    """
    This function is responsible for generating a report based on the provided content.
    
    Args:
        content (str): The content to be used for generating the report.

    Returns:
        str: The generated report.
    """
    try:
        logger.info("Generating report...")

        report_making_agent = create_agent(
            prompt=prompt,
            model=llm,
            tools=[],
            response_format=Report

        )
        response= await report_making_agent.ainvoke(content,return_exceptions=True)
         
        report=response[0]

        if isinstance(report,Exception):
            logger.error(f"Failed to generate report: {report}")
            return None

        logger.info("Report generated successfully.")
        return report    
    
    except Exception as e:
        logger.error(f"Failed to create report agent: {e}")
        return None

