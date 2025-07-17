import requests
from elasticsearch import Elasticsearch

# 读取文本文件
with open("doc/遠野物語.txt", "r") as file:
    text = file.read()

# 调用 Gemini API 获取向量
response = requests.post("https://api.gemini.ai/v1/encode", json={"text": text})
vector = response.json()["vector"]

# 连接到 Elasticsearch
es = Elasticsearch(
    ["https://127.0.0.1:9200"],
    http_auth=("elastic", "AVz2_EK*zDFKJnnem3fi"),
    ca_certs="D:/tools/elasticsearch-9.0.3/config/certs/http_ca.crt",
)

# 存储向量到 Elasticsearch
es.index(index="test-index2", body={"vector": vector})
