from pymilvus import MilvusClient, DataType, Function, FunctionType

client = MilvusClient(
    uri="http://10.60.200.100:19530",
    token="root:Milvus"
)

schema = client.create_schema()

# 文本字段（中文分词）
analyzer_params = {"type": "chinese"}
schema.add_field("id", DataType.INT64, is_primary=True, auto_id=True)
schema.add_field("text", DataType.VARCHAR, max_length=1000, enable_analyzer=True, analyzer_params=analyzer_params)

# 稀疏向量（BM25）
schema.add_field("sparse", DataType.SPARSE_FLOAT_VECTOR)

# 分区键
schema.add_field("key", DataType.VARCHAR, max_length=128, is_partition_key=True)

# 稠密向量
schema.add_field("dense", DataType.FLOAT_VECTOR, dim=2560)

# ✅ 正确写法：启用动态字段
schema.enable_dynamic_field = True

# BM25 函数
bm25_function = Function(
    name="text_bm25_emb",
    input_field_names=["text"],
    output_field_names=["sparse"],
    function_type=FunctionType.BM25
)
schema.add_function(bm25_function)

# 索引
index_params = client.prepare_index_params()
index_params.add_index(
    field_name="sparse",
    index_type="SPARSE_INVERTED_INDEX",
    metric_type="BM25",
    params={"inverted_index_algo": "DAAT_MAXSCORE", "bm25_k1": 1.2, "bm25_b": 0.75}
)
index_params.add_index(
    field_name="dense",
    index_type="HNSW",
    metric_type="COSINE",
)

# 创建集合
client.create_collection(
    collection_name="my_collection112",
    schema=schema,
    index_params=index_params,
    num_partitions=2,
    # properties={"partitionkey.isolation": True}
)
# data = [
#     {
#         "text": "这是第一条文本",
#         "dense": [0.01] * 2560,   # 稠密向量
#         "my_varchar": "partition_1",
#         "meta": {"source": "fileA"}  # 动态 JSON
#     },
#     {
#         "text": "这是第二条文本",
#         "dense": [0.02] * 2560,
#         "my_varchar": "partition_1",
#         "meta": {"source": "fileB", "wt": "qa"}
#     }
# ]
# res = client.insert(collection_name="my_collection112", data=data)
# print(res)
