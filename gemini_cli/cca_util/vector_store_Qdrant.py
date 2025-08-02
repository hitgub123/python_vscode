import datetime
import common_util
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_core.documents import Document


def get_embedding_function(
    embedding_model_name: str, create_custom_embeddings, embedings_model=None
):
    if embedings_model:
        embedding_function = create_custom_embeddings(
            model_name=embedding_model_name, model=embedings_model
        )
    else:
        embedding_function = create_custom_embeddings(model_name=embedding_model_name)
    return embedding_function


def get_vector_store(
    collection_name: str,
    embedding_model_name: str,
    create_custom_embeddings,
    embedings_model,
    qdrant_url: str,
    qdrant_api_key: str,
):
    qdrant_client = QdrantClient(
        url=qdrant_url,
        api_key=qdrant_api_key,
    )
    embedding_function = get_embedding_function(
        embedding_model_name=embedding_model_name,
        create_custom_embeddings=create_custom_embeddings,
        embedings_model=embedings_model,
    )
    vector_store = QdrantVectorStore(
        collection_name=collection_name,
        embedding=embedding_function,
        client=qdrant_client,
    )
    return vector_store, embedding_function


def create_vector_store(
    collection_name: str,
    embedding_model_name: str,
    texts_path,
    create_custom_embeddings,
    embedings_model,
    qdrant_url: str,
    qdrant_api_key: str,
):
    texts = common_util.get_chunks_from_file(texts_path, chunk_size=600, overlap=100)
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

    # Create Qdrant vector store
    # vector_store = QdrantVectorStore.from_documents(
    #     documents=documents,
    #     embedding=embedding_function,
    #     url=qdrant_url,
    #     api_key=qdrant_api_key,
    #     collection_name=collection_name,
    # )

    # if there is too many docs in vector_store,may raise timeout error,
    # so we need to create vector_store in batch,
    # and vector_store got after all loops contains all docs
    batch_size = 128
    for i in range(0, len(documents), batch_size):
        nowtime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{nowtime}]Current : {i} to {i + batch_size} of {len(documents)}")
        vector_store = QdrantVectorStore.from_documents(
            documents=documents[i : i + batch_size],
            embedding=embedding_function,
            url=qdrant_url,
            api_key=qdrant_api_key,
            collection_name=collection_name,
        )
    return vector_store, embedding_function
