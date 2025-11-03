import openai
import asyncio
from typing import List, Union


class OpenAIEmbeddingClient:
    """
    封装 Embedding 请求的异步客户端
    """

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.model = model
        # 初始化异步客户端
        self._async_client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url=base_url
        )

    async def create_embedding(
        self,
        texts: Union[str, List[str]]
    ) -> List[float]:
        """
        异步创建文本向量嵌入
        :param texts: 单个字符串或字符串列表
        :return: 如果是单条输入则返回 List[float]；
                 多条输入则返回 List[List[float]]
        """
        if isinstance(texts, str):
            texts = [texts]

        try:
            response = await self._async_client.embeddings.create(
                model=self.model,
                input=texts
            )
            # 提取所有向量
            embeddings = [item.embedding for item in response.data]
            # 单条输入直接返回一维向量
            return embeddings[0] if len(embeddings) == 1 else embeddings
        except Exception as e:
            print(f"❌ Embedding 请求失败: {e}")
            return []

    async def close(self):
        """
        异步关闭客户端
        """
        await self._async_client.close()
        print("🔒 已关闭 Embedding 异步客户端")


# ================================
# ✅ 使用示例
# ================================
async def main():
    client = OpenAIEmbeddingClient(
        api_key="token-abc123",
        base_url="http://10.60.200.100:2170/v1",
        model="qwen3-embedding"
    )

    texts = ["这是一个测试文本", "这是另一个测试文本"]
    embeddings = await client.create_embedding(texts)
    print(f"✅ 向量数量: {len(embeddings)}")
    print(f"第一个向量前5个值: {embeddings[0][:5]}")

    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
