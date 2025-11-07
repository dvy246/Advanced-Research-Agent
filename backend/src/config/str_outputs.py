import datetime
from typing import Optional
from pydantic import BaseModel,Field
from typing import List

def now_iso():
    """Return current datetime in ISO format including time and timezone if available."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class AnalysisSource(BaseModel):
    source_name: Optional[str] = Field(
        None, description="Name of the data source, e.g., Google, Bing, Reddit, Google Finance", examples=["Google", "Reddit"]
    )
    analysis: str = Field(
        ..., description="Analysis result or summary from this source", min_length=1
    )
    source_link: Optional[str] = Field(
        None, description="Direct link to the information or post", examples=["https://example.com/source"]
    )

    class Config:
        schema_extra = {
            "example": {
                "source_name": "Google",
                "analysis": "The market sentiment is positive based on recent news articles.",
                "source_link": "https://news.google.com/sample-link"
            }
        }


class LLMAnalysisResult(BaseModel):
    sources: List[AnalysisSource] = Field(
        ..., description="List of sources with analysis and URLs", min_items=1
    )
    synthesized_answer: str = Field(
        ..., description="LLM's synthesized answer using all sources", min_length=1
    )

    class Config:
        schema_extra = {
            "example": {
                "sources": [
                    {
                        "source_name": "Google",
                        "analysis": "Positive trend in technology sector.",
                        "source_link": "https://news.google.com/tech"
                    },
                    {
                        "source_name": "Reddit",
                        "analysis": "User discussions corroborate upward momentum.",
                        "source_link": "https://reddit.com/r/stocks"
                    },
                ],
                "synthesized_answer": "There is a general positive outlook on tech stocks based on cross-source analysis."
            }
        }


class Report(BaseModel):
    report: str = Field(
        ..., description="The final report or answer generated", min_length=1
    )
    sources: List[AnalysisSource] = Field(
        default_factory=list,
        description="List of analysis sources with names, details, and links"
    )
    links: List[str] = Field(
        default_factory=list,
        description="Extracted relevant links referenced in the report",
        example=["https://news.google.com/sample-link"]
    )
    proofs: List[str] = Field(
        default_factory=list,
        description="Extracted supporting proofs referenced in the report with the accuracy",
        example=["The current stock price increased by 5% in the last week."]
    )
    generated_at: Optional[str] = Field(
        default_factory=now_iso,
        description="The ISO timestamp when the report was generated"
    )

    class Config:
        schema_extra = {
            "example": {
                "report": "Based on multiple sources, the market is trending upwards.",
                "sources": [
                    {
                        "source_name": "Bing",
                        "analysis": "Recent events have increased confidence in the market.",
                        "source_link": "https://bing.com/news"
                    }
                ],
                "links": [
                    "https://bing.com/news"
                ],
                "proofs": [
                    "Volume of trades increased by 30% over the last month."
                ],
                "generated_at": "2024-06-08T21:15:00.000+00:00"
            }
        }

