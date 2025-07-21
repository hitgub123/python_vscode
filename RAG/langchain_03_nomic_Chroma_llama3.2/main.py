import os, sys

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer
from langchain_community.llms import Ollama

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_util"))
)
import common_util, model_util
import vector_store_Chroma_new


OLLAMA_URL = "http://localhost:11434"


def create_rag_chain(vector_store, embedding_function):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda
    from transformers import AutoTokenizer, AutoModelForCausalLM

    def print_context_and_score(x):
        """
        Print individual documents, their scores, question, and combined context score.
        """
        docs = x["docs"]  # List of Document objects
        query = x["question"]
        context = "\n".join(doc.page_content for doc in docs)  # Combined context
        doc_scores = common_util.score_context(
            query, docs, embedding_function
        )  # Individual scores
        context_score = common_util.score_context(
            query, context, embedding_function
        )  # Combined score

        print("Question:", query)
        print("Individual Documents and Scores:")
        for i, (doc, score) in enumerate(zip(docs, doc_scores)):
            print(f"Doc {i+1} (Score: {score:.3f}):\n{doc.page_content[:1000]}")
        print(f"Context Score: {context_score:.3f}")
        return {"context": context, "question": query}

    # Initialize LLM (replace with your API key)
    # llm = Ollama(model="llama3.2", base_url=OLLAMA_URL, temperature=0)
    tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM3-3B")
    llm = AutoModelForCausalLM.from_pretrained("HuggingFaceTB/SmolLM3-3B")

    # Define RAG prompt
    prompt = ChatPromptTemplate.from_template(
        """You are an assistant for question-answering tasks. Use the following context to answer the question. If you don't know the answer, say so.
        Question: {question}
        Context: {context}
        Answer:"""
    )

    # Create retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    rag_chain = (
        {
            "docs": retriever,  # Pass raw Document list
            "question": RunnablePassthrough(),
        }
        | RunnableLambda(print_context_and_score)
        | prompt
        | llm
    )
    return rag_chain


if __name__ == "__main__":
    # Use a pipeline as a high-level helper
    # Load model directly

    collection_name = "rag_collection"
    embedding_model_name = "nomic-embed-text"
    # embedding_model_name = "bge-m3"
    # embedding = SentenceTransformer(embedding_model_name)
    embedding = HuggingFaceEmbeddings(
        model_name="nomic-ai/nomic-embed-text-v1.5",
        model_kwargs={"device": "cpu", "trust_remote_code": True},
        encode_kwargs={"normalize_embeddings": True},
    )
    texts_path = (
        "doc/Odd John_ A Story Between Jest and Earnest.txt",
        "doc/Pandora.txt",
        # "doc/Odd John_ A Story Between Jest and Earnest-chinese.txt",
    )
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)

    persist_directory = os.path.join(current_dir, "db/chroma_db_1")

    query_mode = 0
    if query_mode:
        vector_store = vector_store_Chroma_new.get_vector_store(
            collection_name=collection_name,
            embedding=embedding,
            persist_directory=persist_directory,
        )
    else:
        vector_store = vector_store_Chroma_new.create_vector_store(
            collection_name=collection_name,
            embedding=embedding,
            texts_path=texts_path,
            persist_directory=persist_directory,
        )

    rag_chain = create_rag_chain(vector_store, embedding)

    # open_webui_util.run_api(rag_chain, vector_store)

    while True:
        query = input("Please enter query (type 'q' to quit): ")
        if query.lower() == "q":
            print("Exiting the program.")
            break
        else:
            common_util.print_search_score(vector_store, query)
            retriever = vector_store.as_retriever(search_kwargs={"k": 5})

            response = rag_chain.invoke(query)
            print(response)
