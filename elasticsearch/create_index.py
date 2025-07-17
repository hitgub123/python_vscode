from elasticsearch import Elasticsearch
import base64
import os

# 连接到 Elasticsearch
es = Elasticsearch(
    ["https://127.0.0.1:9200"],
    http_auth=("elastic", "AVz2_EK*zDFKJnnem3fi"),
    ca_certs="D:/tools/elasticsearch-9.0.3/config/certs/http_ca.crt",
)

def index_file(file_path, index_name="test-index1"):
    try:
        with open(file_path, "rb") as f:
            content = base64.b64encode(f.read()).decode("utf-8")
        doc = {
            "name": os.path.basename(file_path),
            "type": os.path.splitext(file_path)[1][1:].lower(),
            "content": content
        }
        # 索引文件，使用 test1 管道
        response = es.index(index=index_name, body=doc, pipeline="test1")
        print(f"Indexed {file_path}: {response['_id']}")
    except Exception as e:
        print(f"Error indexing {file_path}: {e}")

# 批量索引文件夹中的文件
folder_path = "./doc"  # 替换为你的文件目录
for filename in os.listdir(folder_path):
    file_path = os.path.join(folder_path, filename)
    if filename.lower().endswith(('.pdf', '.doc', '.docx', '.xls', '.xlsx','txt','ppt')):
        index_file(file_path)
