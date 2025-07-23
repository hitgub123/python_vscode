import os, sys
from scipy.spatial.distance import cosine

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_util"))
)
import common_util, embedding_util
from model import model_util
import vector_store_Chroma_new


def calculate_cosine_distances(query, documents, embedding_function):
    query = f"search_query: {query}"
    query_embedding = embedding_function.embed_query(query)
    distances = []
    for doc in documents:
        doc_embedding = embedding_function.embed_documents([doc.page_content])[0]
        distance = cosine(query_embedding, doc_embedding)
        distances.append(distance)
    return distances

def create_rag_chain(vector_store, embedding_function, llm):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain.memory import ConversationBufferMemory
    from langchain.chains import ConversationalRetrievalChain

    memory = ConversationBufferMemory(
        memory_key="chat_history", output_key="answer", return_messages=True
    )
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 5}
    )
    rag_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={
            "prompt": ChatPromptTemplate.from_template(
                """You are an assistant for question-answering tasks. Use the following context and conversation history to answer the question. If you don't know the answer, say so.
                Conversation History: {chat_history}
                Question: {question}
                Context: {context}
                Answer:"""
            )
        },
        return_source_documents=True,
    )
    return rag_chain


if __name__ == "__main__":
    llm = model_util.get_model()

    collection_name = "rag_collection"
    embedding_model_name = "nomic-ai/nomic-embed-text-v1.5"
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

    py_name = common_util.get_py_name()
    persist_directory = os.path.join(current_dir, f"db/{py_name}")

    query_mode = 1
    if query_mode:
        vector_store = vector_store_Chroma_new.get_vector_store(
            collection_name=collection_name,
            embedding=embedding,
            persist_directory=persist_directory,
        )
    else:
        vector_store = vector_store_Chroma_new.create_vector_store_with_textloader(
            collection_name=collection_name,
            embedding=embedding,
            texts_path=texts_path,
            persist_directory=persist_directory,
        )

    rag_chain = create_rag_chain(vector_store, embedding, llm)

    while True:
        query = input("Please enter query (type 'q' to quit): ")
        if query.lower() == "q":
            print("Exiting the program.")
            break
        else:
            response = rag_chain.invoke({"question": query})

            distances = calculate_cosine_distances(query, response["source_documents"], embedding)
            for i, (doc, distance) in enumerate(zip(response["source_documents"], distances)):
                print(f"Doc {i+1} (Cosine Distance: {distance:.3f}):")
                print(f"Content: {doc.page_content[:200]}...")
                print(f"Metadata: {doc.metadata}")            

            print(response["answer"])