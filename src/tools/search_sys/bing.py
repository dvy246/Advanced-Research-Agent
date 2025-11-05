from xxlimited import Str
from aiohttp.web import HTTPException
import os 
import aiohttp
import asyncio
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

class Bing:

    BASE_URL = 'https://serpapi.com/search'

    def __init__(self,user_query:str):
        self._api = os.getenv('SERP_API')
        self.query=user_query

    @classmethod
    def copilot_engine(cls):
        return cls('copilot')

    def create_params(self, engine: str):
        return {
            'engine': engine,
            'q': self.query,
            'api_key': self._api,
            'async': 'true',
        }

    @staticmethod
    async def get_url(session, url, params):
        try:
            async with session.get(url, params=params) as respn:
                if respn.status == 200:
                    data = await respn.json()
                    return data
                else:
                    raise HTTPException(reason=f"Non-200 response: {respn.status}")
        except Exception as e:
            raise HTTPException(reason=str(e))

    async def talk_with_copilot(self):
        try:
            async with aiohttp.ClientSession() as session:
                response = await Bing.get_url(session, Bing.BASE_URL, params=self.create_params(engine='copilot'))
                return response
        except Exception as e:
            print(f'an exception occured at talk with copilot {e}')

    async def bing_search(self):
        try:
            async with aiohttp.ClientSession() as session:
                response = await Bing.get_url(session, Bing.BASE_URL, params=self.create_params('bing'))
                if response:
                    print(response)
                else:
                    return None
        except Exception as e:
            print(f'an exception occured at bing search {e}')


async def bing(user_query:str):
    try:
        bing=Bing(user_query)
        bing_search=asyncio.Task(bing.bing_search())
        if not bing_search:
            print('no bing search data found')
        copilot_talk=asyncio.Task(bing.talk_with_copilot())
        if not copilot_talk:
            print('no copilot data found')
        result=await asyncio.gather(bing_search,copilot_talk,return_exceptions=True)
        if result:
            return result
        else:
            print("No data found")
    except Exception as e:
        print(f'an exception occured at bing {e}')


asyncio.run(bing('what is the latest news about apple'))