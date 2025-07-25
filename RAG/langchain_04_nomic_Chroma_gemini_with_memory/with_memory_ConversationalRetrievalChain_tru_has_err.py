import os, sys
from scipy.spatial.distance import cosine

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_util"))
)
import common_util, embedding_util
from model import model_util
import vector_store_Chroma_new


def get_query_embedding(query, embedding_function):
    """缓存查询嵌入"""
    return embedding_function.embed_query(f"search_query: {query}")


def calculate_cosine_distances(query, documents, embedding_function):
    query_embedding = get_query_embedding(query, embedding_function)
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
    from langchain_core.messages import AIMessage, HumanMessage

    class CustomConversationBufferMemory(ConversationBufferMemory):
        def load_memory_variables(self, inputs):
            history = super().load_memory_variables(inputs)["chat_history"]
            formatted_history = "\n".join(
                (
                    f"Human: {msg.content}"
                    if isinstance(msg, HumanMessage)
                    else f"AI: {msg.content}"
                )
                for msg in history
            )
            return {"chat_history": formatted_history}

    # CustomConversationBufferMemory raise error
    # memory = CustomConversationBufferMemory(
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        output_key="answer",
        return_messages=True,
    )
    retriever = vector_store.as_retriever(
        # search_kwargs={"k": 5, "score_threshold": 0.85}
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
    # def wrapped_chain(inputs):
    #         response = rag_chain.invoke(inputs)
    #         return response["answer"]
    # wrapped_chain.original_chain = rag_chain
    # return wrapped_chain


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
            chunk_size=1000,
            chunk_overlap=100,
        )
    # documents = vector_store._collection.get()['documents']
    rag_chain = create_rag_chain(vector_store, embedding, llm)

    from trulens_eval import Tru, TruChain
    from trulens.core import Feedback
    tru = Tru()
    tru_chain = TruChain(
        rag_chain,
        app_id="RAG_Evaluation",
        # output_variables=1,
        feedbacks=[
            # Feedback.on_context_relevance(),
            # tru.feedback().on_groundedness(),
            # tru.feedback().on_answer_relevance(),_run_output_key
        ],
    )

    eval_data = {"question": [], "answer": [], "contexts": [], "ground_truths": []}

    while True:
        query = input("Please enter query (type 'q' to quit): ")
        if query.lower() == "q":
            print("Exiting the program.")
            break
        else:
            import time
            start_time = time.time()
            with tru_chain as _:
                response = rag_chain(query)
            # response = tru_chain({"question": f"search_query: {query}"})
            print(f"Query time: {time.time() - start_time:.2f} seconds")

            # distances = calculate_cosine_distances(
            #     query, response["source_documents"], embedding
            # )
            # for i, (doc, distance) in enumerate(
            #     zip(response["source_documents"], distances)
            # ):
            #     print(f"Doc {i+1} (Cosine Distance: {distance:.3f}):")
            #     print(f"Content: {doc.page_content[:200]}...")
            #     print(f"Metadata: {doc.metadata}")
            print("Chat History:", response["chat_history"])
            print("\nAnswer:", response["answer"])

            eval_data["question"].append(f"search_query: {query}")
            eval_data["answer"].append(response["answer"])
            eval_data["contexts"].append(
                [doc.page_content for doc in response["source_documents"]]
            )
            eval_data["ground_truths"].append(response["answer"])

    # use RAGAS assessment
    if eval_data["question"]:
        from ragas import evaluate
        from ragas.metrics import (
            context_precision,
            context_recall,
            faithfulness,
            answer_relevancy,
        )
        from datasets import Dataset

        dataset = Dataset.from_dict(eval_data)
        ragas_result = evaluate(
            dataset,
            metrics=[context_precision, context_recall, faithfulness, answer_relevancy],
            llm=llm,
            embeddings=embedding,
        )
        print("\nRAGAS Evaluation Results:")
        print(ragas_result)
