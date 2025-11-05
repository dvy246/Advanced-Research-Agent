import os 
import aiohttp
from aiohttp.web import HTTPException
from dotenv import load_dotenv
import asyncio

load_dotenv()

class GoogleSearch:

    BASE_URL = "https://serpapi.com/search"

    def __init__(self, user_query):
        self.query = user_query
        self._api_key = os.getenv('SERP_API')
        if not self._api_key:
            raise EnvironmentError("SERP_API key missing")

    def build_params(self, engine: str = 'google_light_fast'):

        return {
            "q": self.query,
            'no_cache': 'false',
            'api_key': self._api_key,
            'engine': engine
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

    async def googld_ligh_fast_search(self):
        try:
            params = self.build_params(engine='google_light_fast')
            async with aiohttp.ClientSession() as session:
                response = await C.get_url(session, self.BASE_URL, params)
                return response
        except Exception as e:
            print(e)
            return None

    async def google_news(self):
        try:
            params = self.build_params(engine='google_news')
            async with aiohttp.ClientSession() as session:
                response = await GoogleSearch.get_url(session, self.BASE_URL, params)
                return response
        except Exception as e:
            print(e)
            return None

    async def google_search(self):
        try:
            params = self.build_params(engine='google')
            async with aiohttp.ClientSession() as session:
                response = await GoogleSearch.get_url(session, self.BASE_URL, params)
                return response
        except Exception as e:
            print(e)
            return None


async def google_search(query: str):
    try:
        search_engine = GoogleSearch(user_query=query)
        google_news = asyncio.create_task(search_engine.google_news())
        if not google_news:
            print("No data found for google news")
        google_search_task = asyncio.create_task(search_engine.google_search())
        if not google_search_task:
            print("No data found for google search")
        google_light_fast = asyncio.create_task(search_engine.googld_ligh_fast_search())
        if not google_light_fast:
            print("No data found for google light fast")
        result = await asyncio.gather(
            google_news, google_search_task, google_light_fast, return_exceptions=True
        )
        if result:
            print(f'google result is {result}')
        else:
            print("No data found")
    except Exception as exc:
        print(f"An unexpected error occurred: {exc}")


asyncio.run(google_search('what is the latest news about apple'))