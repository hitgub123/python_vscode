import os, sys

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
import pickle
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from sentence_transformers import SentenceTransformer

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_util"))
)
import common_util


def create_custom_embeddings(model_name, model, pca):
    class CustomEmbeddings(HuggingFaceEmbeddings):
        def embed_documents(self, texts):
            embeddings_768d = model.encode(
                texts, batch_size=32, normalize_embeddings=True
            )
            return pca.transform(embeddings_768d).tolist()

        def embed_query(self, text):
            embedding_768d = model.encode([text], normalize_embeddings=True)[0]
            return pca.transform([embedding_768d]).tolist()[0]

    return CustomEmbeddings(model_name=model_name)


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


def get_embedding_function(embedding_model_name, pca):
    # Initialize sentence-transformers model
    embedding_function = create_custom_embeddings(
        model_name=embedding_model_name,
        model=SentenceTransformer(embedding_model_name),
        pca=pca,
    )
    return embedding_function


def get_vector_store(collection_name, embedding_model_name,persist_directory, pca_model_path):

    pca = get_PCA(pca_model_path)
    embedding_function = get_embedding_function(embedding_model_name, pca)
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embedding_function,
        persist_directory=persist_directory,
    )
    return vector_store


if __name__ == "__main__":
    collection_name = "rag_collection"
    embedding_model_name = "paraphrase-multilingual-mpnet-base-v2"
    texts_path = ("doc/Odd John_ A Story Between Jest and Earnest.txt",)
    current_file_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file_path)
    pca_model_path = os.path.join(current_dir, "model/pca_model.pkl")
    vector_db_path = os.path.join(current_dir, "db/chroma_db_1")
    target_dims = 128

    vector_store = get_vector_store(
        collection_name=collection_name,
        embedding_model_name=embedding_model_name,
        persist_directory=vector_db_path,
        pca_model_path=pca_model_path,
    )
    query = "What is European society?"
    retriever = vector_store.as_retriever(search_kwargs={"k": 5})
    retrieved_docs = retriever.invoke(query)
    context = "\n".join(doc.page_content for doc in retrieved_docs)
    print("Context:\n", context)
    print(1)