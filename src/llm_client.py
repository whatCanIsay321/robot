import openai
import asyncio
from typing import Optional, List, Dict



class OpenAIClient:

    def __init__(self, api_key: str,base_url:str, model: str):
        self.api_key = api_key
        self.model = model
        self._async_client = openai.AsyncOpenAI(api_key=api_key,
                    base_url = base_url)  # 异步客户端


    async def call_async(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        **kwargs
    ) -> str:
        """
        异步调用 Chat API
        """
        try:
            response = await self._async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                **kwargs
            )
            return response
        except Exception as e:
            return f"❌ Error in async call: {str(e)}"

    async def close(self):
        """
        异步关闭 Async 客户端（可选）
        """

        await self._async_client.close()
        print("异步关闭 Async 客户端")
