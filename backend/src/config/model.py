from langchain_google_genai import ChatGoogleGenerativeAI
import os
import asyncio

class Model:
    def __init__(self, model_name: str='gemini-2.5-flash') -> None:
        self.model_name = model_name
        self._api_key = os.getenv('GEMINI_API_KEY')

    def set_model(self):
        """
        Initialize and return an instance of ChatGoogleGenerativeAI.

        Args:
            temperature (float): The temperature parameter for the model, controlling output randomness.

        Returns:
            ChatGoogleGenerativeAI: An instance of the model, or None if instantiation fails.
        """
        try:
            llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                api_key=self._api_key,
                async_client_running=True,
                verbose=True,
            )
            return llm
        except Exception as e:
            # Ideally, use logging instead of print for production code
            print(f"Failed to initialize ChatGoogleGenerativeAI: {e}")
            return None

    async def ask_model(self, query: str, temperature: float = 0.7):
        """
        Submit a query to the model and return the response.

        Args:
            query (str): The input question or prompt.
            temperature (float): Temperature to pass to the model.

        Returns:
            The model's response or None if an error occurs.
        """
        try:
            llm = self.set_model(temperature)
            if llm is None:
                print("Model is not initialized.")
                return None
            response = await llm.ainvoke(query)
            return response
        except Exception as e:
            print(f"Error during model invocation: {e}")
            return None


if __name__=='__main__':
    model=Model()
    async def main(query):
        try:
            model=Model()
            llm=model.set_model()
            response= await llm.ainvoke(query)
            if not response:
                print('no response by model')
        except Exception as e:
            print(f"Error during model invocation: {e}")

asyncio.run(main('hi how are u'))