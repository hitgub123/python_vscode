import os
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA
import numpy as np,pickle


def get_embedings(
    texts, dims=0, model_name="paraphrase-multilingual-mpnet-base-v2", batch_size=32
):
    model = SentenceTransformer(model_name)
    result = model.encode(texts, normalize_embeddings=True, batch_size=batch_size)
    if dims:
        result = change_dims(result, dims)
    return result.tolist()


# def get_one_embeding(text, dims=0, model_name='paraphrase-multilingual-mpnet-base-v2'):
#     model = SentenceTransformer(model_name)
#     result = model.encode(text, normalize_embeddings=True)
#     if dims:
#         result=change_dims(result,dims)
#     return result


def change_dims(embeddings, target_dims):
    # target_dims = 256
    pca = PCA(n_components=target_dims)
    reduced_embeddings = pca.fit_transform(embeddings)
    # Save PCA model tor translate query embeddings to target_dims
    with open("model/pca_model.pkl", "wb") as f:
        pickle.dump(pca, f)
    return reduced_embeddings


if __name__ == "__main__":
    # get_one_embeding('hello world')
    get_embedings(["hello world", "hello word"], dims=32)
