from elasticsearch import Elasticsearch
import os
import es_cloud_util,gemini_api_util


dims = 768
client = Elasticsearch(
    "https://my-elasticsearch-project-a6634e.es.us-east-1.aws.elastic.cloud:443",
    api_key="V1BWMEZwZ0I5UE5nM2tDY3pXS0o6cUxkV1ZMYVlxUEZiMEpaZ3N3em9UQQ==",
)
index_name = "index_file_chunk_overlap"


def update_index_():
    # 批量索引文件夹中的文件
    folder_path = "./doc"  # 替换为你的文件目录
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.lower().endswith(("t.txt")):
            es_cloud_util.index_file_chunk_overlap(client, index_name, file_path, dims)

if __name__ == "__main__":
    update_index_()
    query_kw = "appearance"
    query_embedding = gemini_api_util.get_embedings(query_kw,dims)[0].values
    es_cloud_util.query(client, index_name, query_embedding)
