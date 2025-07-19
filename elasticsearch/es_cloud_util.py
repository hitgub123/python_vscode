from elasticsearch import Elasticsearch, helpers
import es_cloud_util, time, sentence_transformers_util, gemini_api_util
from common_util import gen_md5


def create_index(client, index_name, dims):
    mapping = {
        "mappings": {
            "properties": {
                "vector": {"type": "dense_vector", "dims": dims, "similarity": "cosine"},
            }
        }
    }
    result = client.indices.create(index=index_name, body=mapping)
    print(result)


def update_mapping(client, index_name, dims):
    mapping = {
        "properties": {
            "vector": {"type": "dense_vector", "dims": dims, "similarity": "cosine"},
        }
    }
    mapping_response = client.indices.put_mapping(index=index_name, body=mapping)
    print(mapping_response)


def update_index(client, docs, index_name, dims=768,batch_size=32):
    if not client.indices.exists(index=index_name):
        update_mapping(client, index_name, dims)
    # bulk_response = helpers.bulk(client, docs, index=index_name)
    for i in range(0, len(docs), batch_size):
        chunks = docs[i : i + batch_size]
        print(f"update_index : Current : {i} to {i + batch_size}")
        bulk_response = helpers.bulk(client, chunks, index=index_name)
        print(bulk_response)


def get_property_list(client, index_name, property="md5"):
    if not client.indices.exists(index=index_name):
        return []
    response = client.search(
        index=index_name,
        body={
            "query": {"exists": {"field": "md5"}},
            "fields": [property],
            "_source": False,
            "size": 10000,
        },
    )
    result = [hit["fields"][property][0] for hit in response["hits"]["hits"]]
    return result


def index_file_chunk_overlap(client, index_name, file_path, dims, batch_size=100):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        print(file_path, len(text))
        chunk_size, overlap = 500, 100
        # chunk_size, overlap = 50, 10
        all_chunks = [
            text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)
        ]
        for i in range(0, len(all_chunks), batch_size):
            chunks = all_chunks[i : i + batch_size]  # 每批最多 100 个
            print(f"index_file_chunk_overlap : Current : {i // batch_size}")
            # md5=gen_md5(chunks[0])
            # if md5_exit_check(client,index_name,md5):
            #     print(f"md5 : {md5} exists")
            #     continue
            vectors = gemini_api_util.get_embedings(chunks, dims)
            docs = [
                {"text": chunks[i], "vector": vectors[i].values, "md5": i}
                for i in range(len(chunks))
            ]
            es_cloud_util.update_index(client, docs, index_name)
            if i > 0:
                time.sleep(60)


def index_file_chunk_overlap_sentence_transformers(
    client, index_name, file_path, dims=0
):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
        print(file_path, len(text))
        chunk_size, overlap = 500, 100
        # chunk_size, overlap = 50, 10
        chunks = [
            text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)
        ]
        exist_md5_lst = es_cloud_util.get_property_list(client, index_name)
        chunks = [i for i in chunks if gen_md5(i) not in exist_md5_lst]
        if chunks:
            vectors = sentence_transformers_util.get_embedings(chunks, dims)
            docs = [
                {"text": chunks[i], "vector": vectors[i], "md5": gen_md5(chunks[i])}
                for i in range(len(chunks))
            ]
            es_cloud_util.update_index(client, docs, index_name)


def query(client, index_name, query_embedding):
    body = {
        "size": 3,
        "query": {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                    "params": {"query_vector": query_embedding},
                },
            }
        },
        "highlight": {"fields": {"text": {"pre_tags": ["<b>"], "post_tags": ["</b>"]}}},
    }

    search_response = client.search(
        index=index_name,
        body=body,
    )
    for hit in search_response["hits"]["hits"]:
        print("="*20,"\n",hit["_source"]["text"], "\n", hit["_score"])

    return [hit["_source"]["text"] for hit in search_response["hits"]["hits"]]
