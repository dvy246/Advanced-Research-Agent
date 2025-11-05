import yfinance as yf
import asyncio

class YahooFinance:
    def __init__(self, symbol: str = None, symbols: str = None) -> None:

        self.symbol = symbol
        self.symbols = symbols
        self.ticker = yf.Ticker(self.symbol) if self.symbol else None
        self.tickers = yf.Tickers(self.symbols.upper()) if self.symbols else None

    async def get_history(self, start=None, end=None, interval="1d"):
        if not self.ticker:
            print("Ticker symbol not provided.")
            return None
        try:
            # yfinance's .history is synchronous; wrap in a thread executor
            result = await self.ticker.history(start=start, end=end, interval=interval)
            return result
        except Exception as e:
            print(f"Error fetching history for {self.symbol}: {e}")
            return None

    def get_fundamentals(self):
        if not self.ticker:
            print("Ticker symbol not provided.")
            return None
        try:
            return {
                "info": getattr(self.ticker, "info", None),
                "balance_sheet": getattr(self.ticker, "balance_sheet", None),
                "income_statement": getattr(self.ticker, "income_stmt", None),
                "cashflow": getattr(self.ticker, "cashflow", None),
            }
        except Exception as e:
            print(f"Error fetching fundamentals for {self.symbol}: {e}")
            return None

    def get_corporate_actions(self):
        if not self.ticker:
            print("Ticker symbol not provided.")
            return None
        try:
            return {
                "dividends": getattr(self.ticker, "dividends", None),
                "splits": getattr(self.ticker, "splits", None),
                "shareholders": getattr(self.ticker, "major_holders", None),
                "institutional": getattr(self.ticker, "institutional_holders", None)
            }
        except Exception as e:
            print(f"Error fetching corporate actions for {self.symbol}: {e}")
            return None

    def get_company_info(self):
        if not self.ticker:
            print("Ticker symbol not provided.")
            return None
        try:
            return getattr(self.ticker, "info", None)
        except Exception as e:
            print(f"Error fetching company info for {self.symbol}: {e}")
            return None

    async def companies_analysis_info(self):
        if not self.tickers:
            print("No ticker symbols provided.")
            return None
        try:
            def get_news():
                return self.tickers.news()

            def get_history():
                return self.tickers.history(period='5Y').to_json()

            companies_news = await get_news()
            history = await get_history()

            return {
                'companies_news': companies_news,
                'history': history,
            }
        except Exception as e:
            print(f"Error fetching company analysis info for {self.symbols}: {e}")
            return None


async def yfinance_company(symbol: str):
    try:
        yahoo = YahooFinance(symbol)
        company_info = asyncio.Task(yahoo.get_company_info())
        if not company_info:
            print("No company info found")
        history = asyncio.Task(yahoo.get_history())
        if not history:
            print("No history data found")
        result = await asyncio.gather(company_info, history, return_exceptions=True)
        if not result:
            print("No data found")
        else:
            return result
    except Exception as e:
        print(f"Error in yfinance_company: {e}")

async def yfinance_analysis(symbols: str):
    try:
        yahoo = YahooFinance(symbols)
        analysis = asyncio.Task(yahoo.companies_analysis_info())
        if not analysis:
            print("No analysis data found")
        analysis_result = await asyncio.gather(analysis, return_exceptions=True)
        if not analysis_result:
            print("No data found")
        else:
            return analysis_result
    except Exception as e:
        print(f"Error in yfinance_analysis: {e}")

async def yf_finance(symbol: str):
    try:
        yahoo = YahooFinance(symbol)
        corporate_actions = asyncio.Task(yahoo.get_corporate_actions())
        if not corporate_actions:
            print("No corporate actions data found")
        fundamentals = asyncio.Task(yahoo.get_fundamentals())
        if not fundamentals:
            print("No fundamentals data found")
        result = await asyncio.gather(corporate_actions, fundamentals, return_exceptions=True)
        if not result:
            print("No data found")
        else:
            return result
    except Exception as e:
        print(f"Error in yf_finance: {e}")

async def main(symbol: str = None, query_type: str = None, multi_analysis:bool = None):
    try:
        # Sanity check for inputs
        if query_type is not None:
            lowered_type = query_type.lower()
            if any(keyword in lowered_type for keyword in ['financial_data', 'finance', 'fanalysis']):
                if not symbol:
                    print("Symbol required for financial data")
                    return
                data = await yf_finance(symbol)
                if not data:
                    print("No financial data found")
                    return
                print(data)
                return

        if symbols:
            data = await yfinance_analysis(symbols)
            if not data:
                print("No analysis data found")
                return
            print(data)
            return

        if symbol:
            data = await yfinance_company(symbol)
            if not data:
                print("No company data found")
                return
            print(data)
            return

        print("Please provide either 'symbol' or 'symbols'.")
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main(symbols='AAPL MSFT'))