import common_util, datetime
from langchain_chroma import Chroma


def get_embedding_function(
    embedding_model_name, create_custom_embeddings, embedings_model=None
):
    if embedings_model:
        embedding_function = create_custom_embeddings(
            model_name=embedding_model_name,
            model=embedings_model,
        )
    else:
        embedding_function = create_custom_embeddings(model_name=embedding_model_name)
    return embedding_function


def get_vector_store(
    collection_name,
    embedding_model_name,
    persist_directory,
    create_custom_embeddings,
    embedings_model,
):
    embedding_function = get_embedding_function(
        embedding_model_name=embedding_model_name,
        create_custom_embeddings=create_custom_embeddings,
        embedings_model=embedings_model,
    )
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_function,
        persist_directory=persist_directory,
    )
    return vector_store, embedding_function


def create_vector_store(
    collection_name,
    embedding_model_name,
    texts_path,
    persist_directory,
    create_custom_embeddings,
    embedings_model,
):
    from langchain_core.documents import Document

    texts = common_util.get_chunks_from_file(texts_path, chunk_size=600, overlap=100)

    # Prepare documents for Chroma
    documents = [
        # Document(page_content=texts[i], metadata={"id": common_util.gen_md5(texts[i])})
        Document(page_content=texts[i], id=common_util.gen_md5(texts[i]))
        for i in range(len(texts))
    ]
    embedding_function = get_embedding_function(
        embedding_model_name=embedding_model_name,
        create_custom_embeddings=create_custom_embeddings,
        embedings_model=embedings_model,
    )

    # Create Chroma vector store
    # vector_store = Chroma.from_documents(
    #     documents=documents,
    #     embedding=embedding_function,
    #     collection_name=collection_name,
    #     persist_directory=persist_directory,
    # )
    batch_size = 128
    for i in range(0, len(documents), batch_size):
        nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{nowtime}]Current : {i} to {i + batch_size} of {len(documents)}")
        batch = documents[i : i + batch_size]
        vector_store = Chroma.from_documents(
            documents=batch,
            embedding=embedding_function,
            collection_name=collection_name,
            persist_directory=persist_directory,
        )
    return vector_store, embedding_function
