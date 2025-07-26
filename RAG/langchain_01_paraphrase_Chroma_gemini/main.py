import os, sys

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from langchain_huggingface import HuggingFaceEmbeddings

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_util"))
)
import common_util, vector_store_Chroma, embedding_util


def create_custom_embeddings(model_name, model):
    class CustomEmbeddings(HuggingFaceEmbeddings):
        def embed_documents(self, texts):
            embeddings_768d = model.encode(
                texts, batch_size=32, normalize_embeddings=True
            )
            return embeddings_768d.tolist()

        def embed_query(self, text):
            embedding_768d = model.encode([text], normalize_embeddings=True)[0]
            return embedding_768d.tolist()

    return CustomEmbeddings(model_name=model_name)


def create_rag_chain(vector_store, embedding_function):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_google_genai import ChatGoogleGenerativeAI
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
        # print("Combined Context:\n", context)
        print(f"Context Score: {context_score:.3f}")
        return {"context": context, "question": query}  # Return dict for prompt

    # Initialize LLM (replace with your API key)
    google_api_key = os.environ.get("gemini_api_key2")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", google_api_key=google_api_key, temperature=0
    )

    # Define RAG prompt
    prompt = ChatPromptTemplate.from_template(
        """You are an assistant for question-answering tasks. Use the following context to answer the question. If you don't know the answer, say so.
        Question: {question}
        Context: {context}
        Answer:"""
    )

    # Create retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    # Build RAG chain
    # rag_chain = (
    #     {
    #         "context": retriever
    #         | (lambda docs: "\n".join(doc.page_content for doc in docs)),
    #         "question": RunnablePassthrough(),
    #     }
    #     | prompt
    #     | llm
    # )
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
    collection_name = "rag_collection"
    embedding_model_name = "paraphrase-multilingual-mpnet-base-v2"
    # embedings_model = SentenceTransformer(embedding_model_name)
    embedings_model = embedding_util.get_embedding(
        model_name=embedding_model_name, model_source="sbert"
    )
    texts_path = (
        "doc/Odd John_ A Story Between Jest and Earnest.txt",
        "doc/Pandora.txt",
        # "doc/Odd John_ A Story Between Jest and Earnest-chinese.txt",
    )
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)

    persist_directory = os.path.join(current_dir, "db/chroma_db_1")

    query_mode = 1
    if query_mode:
        vector_store, embedding_function = vector_store_Chroma.get_vector_store(
            collection_name=collection_name,
            embedding_model_name=embedding_model_name,
            persist_directory=persist_directory,
            create_custom_embeddings=create_custom_embeddings,
            embedings_model=embedings_model,
        )
    else:
        vector_store, embedding_function = vector_store_Chroma.create_vector_store(
            collection_name=collection_name,
            embedding_model_name=embedding_model_name,
            texts_path=texts_path,
            persist_directory=persist_directory,
            create_custom_embeddings=create_custom_embeddings,
            embedings_model=embedings_model,
        )

    rag_chain = create_rag_chain(vector_store, embedding_function)

    while True:
        query = input("Please enter query (type 'q' to quit): ")
        if query.lower() == "q":
            print("Exiting the program.")
            break
        else:
            common_util.print_search_score(vector_store, query)
            retriever = vector_store.as_retriever(search_kwargs={"k": 5})

            response = rag_chain.invoke(query)
            print(response.content)
