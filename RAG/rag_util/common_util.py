import hashlib, os, numpy as np


def gen_md5(text):
    hash_value = hashlib.md5(text.encode("utf-8")).hexdigest()
    return hash_value


def get_chunks_from_file(texts_path, chunk_size=500, overlap=100):
    result = []
    for file_path in texts_path:
        print(f"reading {os.path.abspath(file_path)}")
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
            print(file_path, len(text))
            chunks = [
                text[i : i + chunk_size]
                for i in range(0, len(text), chunk_size - overlap)
            ]
            result.extend(chunks)
    return result


def cosine_distance(vec1, vec2):
    """
    Calculate cosine distance between two vectors.
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    cosine_similarity = np.dot(vec1, vec2) / (
        np.linalg.norm(vec1) * np.linalg.norm(vec2)
    )
    return 1 - cosine_similarity


def score_context(query, context, embedding_function):
    """
    Calculate cosine distance between query and context (or individual docs).
    """
    if isinstance(context, list):
        scores = []
        for doc in context:
            doc_embedding = embedding_function.embed_query(doc.page_content)
            query_embedding = embedding_function.embed_query(query)
            scores.append(cosine_distance(query_embedding, doc_embedding))
        return scores
    else:
        query_embedding = embedding_function.embed_query(query)
        context_embedding = embedding_function.embed_query(context)
        return cosine_distance(query_embedding, context_embedding)

    results = vector_store.similarity_search_with_score(query="qux")


def print_search_score(vector_store, query, k=5):
    results = vector_store.similarity_search_with_score(query=query, k=k)
    print('='*20,'print_search_score','='*20)
    for doc, score in results:
        print(f"* [SIM={score:3f}] {doc.page_content} [{doc.metadata}]")
