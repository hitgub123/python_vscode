def get_embedding(
    model_name,
    model_source="huggingface",
    ollama_url="http://localhost:11434",
    trust_remote_code=False,
    model_kwargs=None,
    encode_kwargs={"normalize_embeddings": True},
):
    if model_source == "huggingface":
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs,
        )
    elif model_source == "ollama":
        from langchain_community.embeddings import OllamaEmbeddings

        return OllamaEmbeddings(
            model=model_name,
            base_url=ollama_url,
            model_kwargs=model_kwargs,
        )
    elif model_source == "sbert":
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(
            model_name,
            trust_remote_code=trust_remote_code,
            model_kwargs=model_kwargs,
            # encode_kwargs=encode_kwargs,
        )
    else:
        raise ValueError("Unsupported model source")
