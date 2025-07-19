from elasticsearch import Elasticsearch, helpers
from gemini_api_util import get_embedings
import es_cloud_util, time
from common_util import gen_md5

def update_mapping(client, index_name, dims):
    mappings = {
        "properties": {
            "vector": {"type": "dense_vector", "dims": dims},
            "text": {"type": "text"},
        }
    }
    mapping_response = client.indices.put_mapping(index=index_name, body=mappings)
    print(mapping_response)


def update_index(client, docs, index_name):
    bulk_response = helpers.bulk(client, docs, index=index_name)
    print(bulk_response)

def md5_exit_check(client,index_name,md5):
    response = client.search(
        index=index_name,
        body={
            "query": {
                "term": {
                    "md5": md5
                }
            }
        }
    )
    return response["hits"]["total"]["value"] > 0

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
            md5=gen_md5(chunks[0])
            if md5_exit_check(client,index_name,md5):
                print(f"md5 : {md5} exists")
                continue
            vectors = get_embedings(chunks, dims)
            docs = [
                {"text": chunks[i], "vector": vectors[i].values,"md5":i}
                for i in range(len(chunks))
            ]
            es_cloud_util.update_index(client, docs, index_name)
            if i > 0:
                time.sleep(60)


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
        print(hit["_source"]["text"], "\n", hit["_score"])
