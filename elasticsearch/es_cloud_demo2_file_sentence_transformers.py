from elasticsearch import Elasticsearch
import os
import es_cloud_util, sentence_transformers_util


dims = 768
client = Elasticsearch(
    "https://my-elasticsearch-project-a6634e.es.us-east-1.aws.elastic.cloud:443",
    api_key="V1BWMEZwZ0I5UE5nM2tDY3pXS0o6cUxkV1ZMYVlxUEZiMEpaZ3N3em9UQQ==",
)
index_name = "index_file_chunk_overlap_sentence_transformers"


def update_index_():
    # 批量索引文件夹中的文件
    folder_path = "./doc"  # 替换为你的文件目录
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.lower().endswith(("t.txt")):
            # es_cloud_util.index_file_chunk_overlap_sentence_transformers(client, index_name, file_path, dims)
            es_cloud_util.index_file_chunk_overlap_sentence_transformers(
                client, index_name, file_path
            )


if __name__ == "__main__":
    # update_index_()

    query_kw = "religion of nationalism"
    query_embedding = sentence_transformers_util.get_embedings([query_kw])[0]
    es_cloud_util.query(client, index_name, query_embedding)

    # es_cloud_util.get_property_list(client, index_name)
