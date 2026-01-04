# app/infra/milvus.py


import threading

from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

_milvus_lock = threading.Lock()
_initialized = False


def init_milvus(host: str, port: int | str, dim: int) -> None:
    global _initialized
    if _initialized:
        return

    with _milvus_lock:
        if _initialized:
            return

        # connect (idempotent하게 한 번만)
        connections.connect(alias="default", host=host, port=str(port))

        ensure_collections(dim)
        _initialized = True


def _ensure_collection(name: str, dim: int) -> None:
    if utility.has_collection(name):
        col = Collection(name=name)
        # 이미 존재하면 load만 보장 (원하면 index 유무도 검사 가능)
        col.load()
        return

    fields = [
        FieldSchema(name="chunk_id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim),
        FieldSchema(name="source_type", dtype=DataType.VARCHAR, max_length=32),
        FieldSchema(name="updated_at", dtype=DataType.INT64),
    ]
    schema = CollectionSchema(fields=fields, description="koo rag chunks")
    col = Collection(name=name, schema=schema)

    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "COSINE",
        "params": {"nlist": 1024},
    }
    col.create_index(field_name="embedding", index_params=index_params)
    col.load()


def ensure_collections(dim: int) -> None:
    _ensure_collection("koo_cs_chunks", dim)
    _ensure_collection("koo_dev_chunks", dim)


def get_collection(name: str) -> Collection:
    # init_milvus()가 먼저 호출된다는 가정
    return Collection(name=name)
