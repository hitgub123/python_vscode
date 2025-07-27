

docs=['a', 'b', 'c', 'd', 'e']
scores=[3,4, 2, 5,1]
# Sort documents by reranker scores
sorted_docs_with_scores = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
sorted_docs = [doc for doc, _ in sorted_docs_with_scores]
reranker_scores = [score for _, score in sorted_docs_with_scores]