import os, sys

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from langchain_community.llms import Ollama
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_util"))
)
import common_util, embedding_util
import vector_store_Chroma_new


OLLAMA_URL = "http://localhost:11434"


def create_rag_chain(vector_store, embedding_function,llm):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda

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
    model_name = "HuggingFaceTB/SmolLM3-3B"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=128)
    llm = HuggingFacePipeline(pipeline=pipe, model_kwargs={"temperature": 0})

    collection_name = "rag_collection"
    embedding_model_name = "nomic-ai/nomic-embed-text-v1.5"
    # embedding_model_name = "bge-m3"
    embedding = embedding_util.get_embedding(
        model_name=embedding_model_name,
        model_kwargs={"device": "cpu", "trust_remote_code": True},
        encode_kwargs={"normalize_embeddings": True},
    )
    texts_path = (
        "doc/Odd John_ A Story Between Jest and Earnest.txt",
        "doc/Pandora.txt",
    )
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)

    persist_directory = os.path.join(current_dir, "db/main_without_ollama")

    query_mode = 1
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

    rag_chain = create_rag_chain(vector_store, embedding,llm)

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
