from pymilvus import MilvusClient, DataType, Function, FunctionType

client = MilvusClient(
    uri="http://10.60.200.100:19530",
    token="root:Milvus"
)

# --------------------------
# 1️⃣ 创建 Schema
# --------------------------
schema = client.create_schema()

# 文本字段（支持中文分词）
analyzer_params = {"type": "chinese"}
schema.add_field(
    field_name="id",
    datatype=DataType.INT64,
    is_primary=True,
    auto_id=True
)
schema.add_field(
    field_name="text",
    datatype=DataType.VARCHAR,
    max_length=1000,
    enable_analyzer=True,
    analyzer_params=analyzer_params
)

# 稀疏向量 (BM25)
schema.add_field(
    field_name="sparse",
    datatype=DataType.SPARSE_FLOAT_VECTOR
)

# 分区键
schema.add_field(
    field_name="my_varchar",
    datatype=DataType.VARCHAR,
    max_length=128,
    is_partition_key=True
)

# --------------------------
# 2️⃣ 新增 Dense 向量字段
# --------------------------
schema.add_field(
    field_name="dense",
    datatype=DataType.FLOAT_VECTOR,
    dim=2560  # 稠密向量维度
)

# --------------------------
# 3️⃣ 新增动态 JSON 字段
# --------------------------
schema.enable_dynamic_field(True)  # 允许动态字段（Meta JSON）
# 或者你也可以固定一个 JSON 字段：
# schema.add_field(field_name="meta", datatype=DataType.JSON)

# --------------------------
# 4️⃣ 定义 BM25 自动编码函数
# --------------------------
bm25_function = Function(
    name="text_bm25_emb",
    input_field_names=["text"],
    output_field_names=["sparse"],
    function_type=FunctionType.BM25
)
schema.add_function(bm25_function)

# --------------------------
# 5️⃣ 定义索引参数
# --------------------------
index_params = client.prepare_index_params()

# 稀疏索引
index_params.add_index(
    field_name="sparse",
    index_type="SPARSE_INVERTED_INDEX",
    metric_type="BM25",
    params={
        "inverted_index_algo": "DAAT_MAXSCORE",
        "bm25_k1": 1.2,
        "bm25_b": 0.75
    }
)

# 稠密向量索引（HNSW / IVF_FLAT 均可）
index_params.add_index(
    field_name="dense",
    index_type="HNSW",
    metric_type="COSINE",
    params={
        "M": 32,
        "efConstruction": 200
    }
)

# --------------------------
# 6️⃣ 创建 Collection
# --------------------------
client.create_collection(
    collection_name="my_collection12",
    schema=schema,
    index_params=index_params,
    num_partitions=16,
)
# data = [
#     {
#         "text": "这是一个测试文本",
#         "dense": [0.1] * 2560,
#         "my_varchar": "partition_1",
#         "meta": {"source": "doc1", "category": "news"}  # 动态 JSON 字段
#     },
#     {
#         "text": "另一个文本样本",
#         "dense": [0.2] * 2560,
#         "my_varchar": "partition_2",
#         "meta": {"source": "doc2", "main": "qa"}
#     }
# ]
#
# client.insert(collection_name="my_collection12", data=data)
