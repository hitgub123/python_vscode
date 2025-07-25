import os, sys

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_util"))
)
import common_util, embedding_util,test_util
from model import model_util
import vector_store_Chroma_new


def create_rag_chain(vector_store, embedding_function, llm):
    from langchain_core.prompts import ChatPromptTemplate
    from langchain_core.runnables import RunnablePassthrough, RunnableLambda
    from langchain.memory import ConversationBufferMemory
    from langchain_core.messages import AIMessage, HumanMessage

    memory = ConversationBufferMemory(return_messages=True)

    def print_context_and_score(x):
        docs = x["docs"]
        query = x["question"]
        context = [doc.page_content for doc in docs]
        context_str = "\n".join(context)
        doc_content_scores = common_util.score_context(query, docs, embedding_function)
        context_score = common_util.score_context(query, context_str, embedding_function)

        print("Question:", query)
        print("Individual Documents and Scores:")
        for i, (doc, score) in enumerate(zip(docs, doc_content_scores)):
            print(
                f"{">"*20} \nDoc {i+1} (Score: {score:.3f}):\n{doc.page_content[:1000]}"
            )
        print(f"Context Score: {context_score:.3f}")
        return {"context": context, "question": query}

    def read_history(x):
        history = memory.load_memory_variables({})["history"]
        formatted_history = "\n".join(
            (
                f"Human: {msg.content}"
                if isinstance(msg, HumanMessage)
                else f"AI: {msg.content}"
            )
            for msg in history
        )
        return {
            "context": x["context"],
            "question": x["question"],
            "history": formatted_history,
        }

    # Define RAG prompt
    prompt = ChatPromptTemplate.from_template(
        """You are an assistant for question-answering tasks. Use the following context and conversation history to answer the question. If you don't know the answer, say so.
        Conversation History: {history}        
        Question: {question}
        Context: {context}
        Answer:"""
    )

    # Create retriever
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})

    def save_to_memory(x):
        memory.save_context({"input": x["question"]}, {"output": x["answer"]})
        return {"answer": x["answer"], "context": x["context"]}

    rag_chain = (
        {
            "docs": retriever,  # Pass raw Document list
            "question": RunnablePassthrough(),
        }
        | RunnableLambda(print_context_and_score)
        | RunnableLambda(read_history)
        # | prompt
        # | llm
        # | RunnableLambda(lambda x: {"answer": x.content, "question": x.metadata["question"]})
        | RunnableLambda(
            lambda x: {
                "prompt": prompt.invoke(x),
                "question": x["question"],
                "context": x["context"],
            }
        )
        | RunnableLambda(
            lambda x: {
                "answer": llm.invoke(x["prompt"]).content,
                "question": x["question"],
                "context": x["context"],
            }
        )
        | RunnableLambda(save_to_memory)
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

    # while True:
    #     query = input("Please enter query (type 'q' to quit): ")
    #     if query.lower() == "q":
    #         print("Exiting the program.")
    #         break
    #     else:
    #         import time

    #         start_time = time.time()
    #         response = rag_chain.invoke(f"search_query: {query}")
    #         print(f"查询耗时: {time.time() - start_time:.2f} 秒")
    #         print("\n回答:", response["answer"])

    # RAGAS 评估
    test_util.test_llm(rag_chain)
