"""
This module provides an asynchronous Python interface to fetch stock and financial markets data
via SerpAPI's Google Finance engine. It includes parameter building for flexible symbol, trend,
and index queries, and robust error handling for API and networking failures.
"""

import aiohttp
import os
import asyncio
from typing import Optional
from aiohttp.web_exceptions import HTTPException
from dotenv import load_dotenv

load_dotenv()

class GoogleFinanceData:
    """
    Asynchronous client to interact with the SerpAPI Google Finance endpoint for retrieving
    financial information about equities and markets. Supports parameter customization for 
    symbol lookups, trend windows, and market indices.
    """

    BASE_URL = "https://serpapi.com/search"

    def __init__(self, symbol, trend: Optional[str] = None, index_market: Optional[str] = None):
        self._api_key = os.getenv('SERP_API')
        if not self._api_key:
            raise EnvironmentError("SERP_API key missing")
        self.symbol = symbol
        self.trend = trend
        self.index = index_market

    def build_serpapi_params(self) -> dict:
        """
        Constructs parameters for a SerpAPI Google Finance API call based on current settings.

        Returns:
            dict: Parameters suitable for the API query.
        """
        if not self.trend and not self.index:
            return {
                "engine": "google_finance",
                "q": self.symbol,
                "api_key": self._api_key,
                'window': 'MAX',
                'async': 'true',
                'no_cache': 'false',
            }
        elif self.trend and self.index:
            return {
                "engine": "google_finance",
                "q": self.symbol,
                "api_key": self._api_key,
                'window': '5Y',
                'async': 'true',
                'no_cache': 'false',
                'trend': self.trend,
                'index_market': self.index,
            }
        elif self.trend:
            return {
                "engine": "google_finance",
                "q": self.symbol,
                "api_key": self._api_key,
                'window': 'MAX',
                'async': 'true',
                'no_cache': 'false',
                'trend': self.trend,
            }
        elif self.index:
            return {
                "engine": "google_finance",
                "api_key": self._api_key,
                'window': '5Y',
                'async': 'true',
                'no_cache': 'false',
                'index_market': self.index,
            }
    @staticmethod
    async def get_url(session, url, params):
        try:

            async with session.get(url, params=params) as respn:
                if respn.status == 200:
                    data=await respn.json()
                    return data
                else:
                    raise HTTPException(
                        reason=f"Non-200 response: {respn.status}", status_code=respn.status
                    )
        except Exception as e:
            raise HTTPException(reason=str(e), status_code=500)

    async def fetch_google_finance_data(self) -> dict:
        """
        Asynchronously fetches financial data for a symbol from the SerpAPI Google Finance engine.

        Returns:
            dict: Parsed JSON data returned by the API.

        Raises:
            Exception: For any errors during API fetch.
        """
        params = self.build_serpapi_params()
        try:
            async with aiohttp.ClientSession() as session:
                data = await GoogleFinanceData.get_url(session, self.BASE_URL, params)
                if data is None:
                    raise Exception("Failed to fetch financial data from SerpAPI.")
                return data
        except Exception as exc:
            print(f"Unexpected error during SerpAPI fetch: {exc}")
            raise

    async def fetch_financial_markets_data(self) -> dict:
        """
        Asynchronously fetches financial markets data from SerpAPI and extracts primary 
        search parameters and market graph data, if available.

        Returns:
            dict: Contains 'search_parameters' and 'graph' from the API response.

        Raises:
            Exception: For any errors during data retrieval.
        """
        params = self.build_serpapi_params()
        try:
            async with aiohttp.ClientSession() as session:
                data = await GoogleFinanceData.get_url(session, self.BASE_URL, params)
                if data is None:
                    raise Exception("Failed to fetch market data from SerpAPI.")
                return data
        except Exception as exc:
            print(f"Error occurred while retrieving financial market data: {exc}")
            raise


async def google_finance(symbol: str,trend: Optional[str] = None, index_market: Optional[str] = None):
    gf=GoogleFinanceData(symbol=symbol,trend=trend,index_market=index_market)
    finance_data=asyncio.create_task(gf.fetch_google_finance_data())
    if not finance_data:
        print("No data found for finance")
    financia_markets=asyncio.create_task(gf.fetch_financial_markets_data())
    if not financia_markets:
        print("No data found for finance markets")
    result=await asyncio.gather(finance_data,financia_markets,return_exceptions=True)
    if result:
        print(result)
    else:
        print("No data found")


asyncio.run(google_finance("AAPL"))