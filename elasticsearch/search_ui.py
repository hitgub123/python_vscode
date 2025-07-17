from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch(["http://127.0.0.1:9200"])

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    body = {
        "query": {
            "match": {
                "attachment.content": query
            }
        },
        "highlight": {
            "fields": {
                "attachment.content": {}
            }
        }
    }
    results = es.search(index="documents", body=body)
    return jsonify(results['hits']['hits'])

if __name__ == '__main__':
    app.run(port=5000)