import datetime
import pickle
import common_util
from langchain_chroma import Chroma


def get_PCA(pca_model_path):

    with open(pca_model_path, "rb") as f:
        pca = pickle.load(f)
    return pca


def update_PCA(pca_model_path, embedings_model, texts, target_dims):
    from sklearn.decomposition import PCA

    # Generate 768D embeddings
    embeddings_768d = embedings_model.encode(
        texts, batch_size=32, normalize_embeddings=True
    )

    # Train PCA (128 dimensions)
    pca = PCA(n_components=target_dims)
    _ = pca.fit_transform(embeddings_768d)

    # Save PCA model
    with open(pca_model_path, "wb") as f:
        pickle.dump(pca, f)

    return pca


def get_embedding_function(
    embedding_model_name, pca, create_custom_embeddings, embedings_model
):
    # Initialize sentence-transformers model
    if embedings_model:
        embedding_function = create_custom_embeddings(
            model_name=embedding_model_name,
            # model=SentenceTransformer(embedding_model_name),
            model=embedings_model,
            pca=pca,
        )
    else:
        embedding_function = create_custom_embeddings(
            model_name=embedding_model_name, pca=pca
        )
    return embedding_function


def get_vector_store(
    collection_name,
    embedding_model_name,
    persist_directory,
    pca_model_path,
    create_custom_embeddings,
    embedings_model,
):
    pca = None
    if pca_model_path:
        pca = get_PCA(pca_model_path)
    embedding_function = get_embedding_function(
        embedding_model_name=embedding_model_name,
        pca=pca,
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
    pca_model_path,
    persist_directory,
    target_dims,
    create_custom_embeddings,
    embedings_model,
):
    from langchain_core.documents import Document

    texts = common_util.get_chunks_from_file(texts_path, chunk_size=600, overlap=100)

    # Prepare documents for Chroma
    documents = [
        Document(page_content=texts[i], metadata={"id": common_util.gen_md5(texts[i])})
        for i in range(len(texts))
    ]

    pca = None
    if pca_model_path:
        pca = update_PCA(
            pca_model_path=pca_model_path,
            # embedings_model=SentenceTransformer(embedding_model_name),
            embedings_model=embedings_model,
            texts=texts,
            target_dims=target_dims,
        )

    embedding_function = get_embedding_function(
        embedding_model_name=embedding_model_name,
        pca=pca,
        create_custom_embeddings=create_custom_embeddings,
        embedings_model=embedings_model,
    )

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

    # vector_store = Chroma.from_documents(
    #     documents=documents,
    #     embedding=embedding_function,
    #     collection_name=collection_name,
    #     persist_directory=persist_directory,
    # )
    return vector_store, embedding_function
