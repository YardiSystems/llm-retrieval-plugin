import random
import time

from pymilvus import (
    connections,
    FieldSchema, CollectionSchema, DataType,
    Collection,
    utility,
)

_HOST = '127.0.0.1'
_PORT = '19530'

if __name__ == '__main__':
    connections.connect(host=_HOST, port=_PORT)

    dim = 512
    collection_name = "test"
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)

    field1 = FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False)
    field2 = FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=dim)
    schema = CollectionSchema(fields=[field1, field2])
    collection = Collection(name=collection_name, schema=schema)
    print("\ncollection created:", collection_name)

    index_param = {
        "index_type": "IVF_FLAT",
        "params": {"nlist": 256},
        "metric_type": "L2"}
    collection.create_index("embedding", index_param)

    num = 10000
    data = [
        [i for i in range(num)],
        [[random.random() for _ in range(dim)] for _ in range(num)],
    ]
    collection.insert(data)
    collection.flush()
    print("Insert", num, "vectors")
    print("Collection row count:", collection.num_entities)

    start = time.time()
    collection.load()
    end = time.time()
    print("Load collection, time cost:", (end-start)*1000, "ms")