import common_util, datetime
from langchain_chroma import Chroma


def get_vector_store(
    collection_name,
    embedding,
    persist_directory,
):
    vector_store = Chroma(
        collection_name=collection_name,
        embedding_function=embedding,
        persist_directory=persist_directory,
    )
    return vector_store


def create_vector_store(
    collection_name,
    embedding,
    persist_directory,
    texts_path,
):
    from langchain_core.documents import Document

    texts = common_util.get_chunks_from_file(texts_path, chunk_size=600, overlap=100)
    # Prepare documents for Chroma
    documents = [
        Document(page_content=texts[i], id=common_util.gen_md5(texts[i]))
        for i in range(len(texts))
    ]

    # Create Chroma vector store
    # vector_store = Chroma.from_documents(
    #     documents=documents,
    #     embedding=embedding,
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
            embedding=embedding,
            collection_name=collection_name,
            persist_directory=persist_directory,
        )
    return vector_store


def create_vector_store_with_textloader(
    collection_name, embedding, persist_directory, texts_path
):
    from langchain_community.document_loaders import TextLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    documents = []
    for path in texts_path:
        loader = TextLoader(path,encoding="utf-8")
        docs = loader.load()
        documents.extend(docs)

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = splitter.split_documents(documents)
    for obj in texts:
        obj.page_content = f"search_document: {obj.page_content}"

    vector_store = Chroma.from_documents(
        documents=texts,
        embedding=embedding,
        collection_name=collection_name,
        persist_directory=persist_directory,
    )
    return vector_store
