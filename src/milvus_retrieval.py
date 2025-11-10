import asyncio
from typing import List, Dict, Any, Optional, Union
from pymilvus import AsyncMilvusClient


class MilvusHybridRetriever:
    """
    🔍 Milvus 混合检索器 (Dense + BM25 + RRF/WeightedRank)
    支持异步 + 批量输入 + 同块合并。
    """

    def __init__(
        self,
        uri: str,
        token: str,
        default_top_k: int = 5,
        default_search_params: Optional[Dict[str, Any]] = None,
    ):
        self.async_client = AsyncMilvusClient(uri=uri, token=token)
        self.default_top_k = default_top_k
        self.default_search_params = default_search_params or {
            "params": {"drop_ratio_search": 0.2}
        }

    # ===========================================================
    # 🔹 BM25 Search (内部合并)
    # ===========================================================
    async def bm25_search(
        self,
        collection_name: str,
        queries: Union[str, List[str]],
        top_k: Optional[int] = None,
        output_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        top_k = top_k or self.default_top_k
        output_fields = output_fields or ["text"]

        if isinstance(queries, str):
            queries = [queries]

        try:
            res = await self.async_client.search(
                collection_name=collection_name,
                data=queries,
                anns_field="bm25",
                search_params=self.default_search_params,
                limit=top_k,
                output_fields=output_fields,
            )
            return self._merge_same_chunk(res, source="bm25")
        except Exception as e:
            print(f"❌ BM25 搜索失败: {e}")
            return []

    # ===========================================================
    # 🔹 Dense Search (内部合并)
    # ===========================================================
    async def dense_search(
        self,
        collection_name: str,
        query_vectors: Union[List[float], List[List[float]]],
        top_k: Optional[int] = None,
        output_fields: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        top_k = top_k or self.default_top_k
        output_fields = output_fields or ["text"]

        if isinstance(query_vectors[0], (int, float)):
            query_vectors = [query_vectors]

        res = await self.async_client.search(
            collection_name=collection_name,
            data=query_vectors,
            anns_field="embedding",
            limit=top_k,
            output_fields=output_fields,
        )
        return self._merge_same_chunk(res, source="dense")

    # ===========================================================
    # 🔹 同块结果合并逻辑
    # ===========================================================
    @staticmethod
    def _merge_same_chunk(res: Any, source: str) -> List[Dict[str, Any]]:
        """
        对相同 chunk（相同 id 或 text）合并得分
        输出：按合并后总得分降序排序
        """
        if not res:
            return []

        chunk_scores: Dict[str, Dict[str, Any]] = {}

        for hits in res:  # 每个 query 的结果
            for hit in hits:
                text = None
                if hasattr(hit, "entity") and hasattr(hit.entity, "get"):
                    text = hit.entity.get("text")
                elif isinstance(getattr(hit, "entity", None), dict):
                    text = hit.entity.get("text")
                chunk_id = getattr(hit, "id", text)  # 优先用 id
                score = getattr(hit, "score", 0.0)

                if chunk_id not in chunk_scores:
                    chunk_scores[chunk_id] = {
                        "id": chunk_id,
                        "text": text,
                        "merged_score": score,
                        "count": 1,
                        "source": source,
                    }
                else:
                    # 叠加得分
                    chunk_scores[chunk_id]["merged_score"] += score
                    chunk_scores[chunk_id]["count"] += 1

        merged_list = list(chunk_scores.values())
        # 按合并得分降序排列
        merged_list.sort(key=lambda x: x["merged_score"], reverse=True)
        return merged_list

    async def close(self):
        await self.async_client.close()


# ===========================================================
# 🔹 Example Usage
# ===========================================================
async def main():
    retriever = MilvusHybridRetriever(
        uri="http://10.60.200.100:19530",
        token="root:Milvus",
        default_top_k=3,
    )

    queries = [
        "bright day grace speed grace runs day jumps silent speed horizon lazy dog",
        "bright day grace speed grace runs day jumps silent speed horizon lazy dog",
    ]

    print("\n--- 🔍 BM25 Search (Merged Same Chunk) ---")
    bm25_results = await retriever.bm25_search("documents", queries)
    for r in bm25_results:
        print(f"ChunkID: {r['id']} | ScoreSum: {r['merged_score']:.4f} | Count: {r['count']} | Text: {r['text'][:60]}...")

    await retriever.close()


if __name__ == "__main__":
    asyncio.run(main())
    print("✅ Done.")
