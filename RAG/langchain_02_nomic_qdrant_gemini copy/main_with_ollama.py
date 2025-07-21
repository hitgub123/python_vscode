import os, sys

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from langchain_community.embeddings import OllamaEmbeddings

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_util"))
)
import common_util, account

QDRANT_URL = account.QDRANT_URL
QDRANT_API_KEY = account.QDRANT_API_KEY

OLLAMA_URL = "http://localhost:11434"

def create_custom_embeddings(model_name):
    class CustomEmbeddings(OllamaEmbeddings):
        def embed_documents(self, texts):
            embeddings= super().embed_documents(texts)
            return embeddings

        def embed_query(self, text):
            embedding = super().embed_documents(text)
            return embedding

    return CustomEmbeddings(model=model_name, base_url=OLLAMA_URL)


def get_embedding_function(embedding_model_name):
    embedding_function = create_custom_embeddings(model_name=embedding_model_name)
    return embedding_function


def create_vector_store(
    collection_name,
    embedding_model_name,
    texts_path,
):
    texts = common_util.get_chunks_from_file(texts_path, chunk_size=600, overlap=100)
    documents = [
        Document(page_content=texts[i], metadata={"id": common_util.gen_md5(texts[i])})
        for i in range(len(texts))
    ]

    embedding_function = get_embedding_function(embedding_model_name)

    # Create Qdrant vector store
    vector_store = QdrantVectorStore.from_documents(
        documents=documents,
        embedding=embedding_function,
        url=QDRANT_URL,
        api_key=QDRANT_API_KEY,
        collection_name=collection_name,
    )
    return vector_store, embedding_function


def get_vector_store(collection_name, embedding_model_name, qdrant_client):
    embedding_function = get_embedding_function(embedding_model_name)
    vector_store = QdrantVectorStore(
        collection_name=collection_name,
        embedding=embedding_function,
        client=qdrant_client,
    )
    return vector_store, embedding_function


def create_rag_chain(vector_store, embedding_function):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda

    def print_context_and_score(x):
        docs = x["docs"]
        query = x["question"]
        context = "\n".join(doc.page_content for doc in docs)
        doc_scores = common_util.score_context(query, docs, embedding_function)
        context_score = common_util.score_context(query, context, embedding_function)

        print("Question:", query)
        print("Individual Documents and Scores:")
        for i, (doc, score) in enumerate(zip(docs, doc_scores)):
            print(
                ">" * 40,
                f"\nDoc {i+1} (Score: {score:.3f}):\n{doc.page_content[:1000]}",
            )
        print(f"Context Score: {context_score:.3f}")
        return {"context": context, "question": query}

    google_api_key = os.environ.get("gemini_api_key2")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", google_api_key=google_api_key, temperature=0
    )

    prompt = ChatPromptTemplate.from_template(
        """You are an assistant for question-answering tasks. Use the following context to answer the question. If you don't know the answer, say so.
        Question: {question}
        Context: {context}
        Answer:"""
    )

    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    rag_chain = (
        {
            "docs": retriever,
            "question": RunnablePassthrough(),
        }
        | RunnableLambda(print_context_and_score)
        | prompt
        | llm
    )
    return rag_chain


if __name__ == "__main__":
    collection_name = "rag_collection_ollama"
    embedding_model_name = "nomic-embed-text"
    texts_path = (
        "doc/Odd John_ A Story Between Jest and Earnest.txt",
        "doc/Pandora.txt",
    )

    query_mode = 0
    if query_mode:
        qdrant_client = QdrantClient(
            url=QDRANT_URL,
            api_key=QDRANT_API_KEY,
        )
        vector_store, embedding_function = get_vector_store(
            collection_name=collection_name,
            embedding_model_name=embedding_model_name,
            qdrant_client=qdrant_client,
        )
    else:
        vector_store, embedding_function = create_vector_store(
            collection_name=collection_name,
            embedding_model_name=embedding_model_name,
            texts_path=texts_path,
        )

    rag_chain = create_rag_chain(vector_store, embedding_function)

    while True:
        query = input("Please enter query (type 'q' to quit): ")
        if query.lower() == "q":
            print("Exiting the program.")
            break
        else:
            common_util.print_search_score(vector_store, query)
            response = rag_chain.invoke(query)
            print(response.content)
