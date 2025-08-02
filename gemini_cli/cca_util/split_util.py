import os, sys
from llama_index.core.schema import Document

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_util"))
)

gemini_api_key=os.environ.get("gemini_api_key3")

def split_token_chunks(text, chunk_size=700, overlap=100):
    """
    基于 Token 的滑动窗口分块。

    Args:
        text: 输入文本
        chunk_size: 每个块的最大 Token 数（默认 700）
        overlap: 块之间的重叠 Token 数（默认 100）

    Returns:
        分割后的文本块列表
    """
    import tiktoken

    tokenizer = tiktoken.get_encoding("cl100k_base")

    tokens = tokenizer.encode(text, disallowed_special=())

    result = []
    step = chunk_size - overlap

    for i in range(0, len(tokens), step):
        chunk_tokens = tokens[i : i + chunk_size]
        chunk_text = tokenizer.decode(chunk_tokens)
        result.append(chunk_text)

    return result


def split_text_chunks(text, chunk_size=700, overlap=100):
    result = [
        text[i : i + chunk_size] for i in range(0, len(text), chunk_size - overlap)
    ]
    return result


def split_RecursiveCharacterTextSplitter(text, chunk_size=700, overlap=100):
    from langchain.text_splitter import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=overlap
    )
    result = splitter.split_text(text)
    return result


# SentenceSplitter 是一种基于结构和长度的分割器，它确保块边界在句子的自然结束点上，而不是在句子中间截断。它不理解文本的深层含义或语义连贯性。
def get_chunks_from_file_SentenceSplitter(text, chunk_size=700, overlap=100):
    from llama_index.core.node_parser import SentenceSplitter

    splitter = SentenceSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
    )

    doc = Document(text=text)

    nodes = splitter.get_nodes_from_documents([doc])

    result = [node.text for node in nodes]

    return result,nodes


def get_chunks_from_file_SemanticSplitter(text,embed_model=None):
    from llama_index.core.node_parser import SemanticSplitterNodeParser
    if not embed_model:
        from llama_index.embeddings.huggingface import HuggingFaceEmbedding
        # embed_model = HuggingFaceEmbedding(model_name="paraphrase-multilingual-mpnet-base-v2")
        embed_model = HuggingFaceEmbedding(model_name="nomic-ai/nomic-embed-text-v1.5",trust_remote_code=True)
        # embed_model = HuggingFaceEmbedding(model_name="nomic-ai/nomic-bert-2048",trust_remote_code=True)
        
        # from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
        # embed_model = GoogleGenAIEmbedding(
            # model_name="gemini-embedding-001", api_key=gemini_api_key)
        # )

    splitter = SemanticSplitterNodeParser(
        buffer_size=1,  # 每块至少包含 1 句话
        embed_model=embed_model,
        include_metadata=True,
        include_prev_next_rel=True,
        breakpoint_percentile_threshold=75,  # 语义断点阈值
    )

    doc = Document(text=text)

    nodes = splitter.get_nodes_from_documents([doc])

    chunk_texts = [node.text for node in nodes]

    return chunk_texts,nodes


if __name__ == "__main__":
    files = ["doc/唐诗三百首.txt", "doc/Pandora.txt"]
    with open(files[1], "r", encoding="utf-8") as f:
        text = f.read()
        # result = split_token_chunks(text)
        # result = split_text_chunks(text)
        # result = split_RecursiveCharacterTextSplitter(text)
        # result = get_chunks_from_file_SentenceSplitter(text)
        result = get_chunks_from_file_SemanticSplitter(text)
        print(result)
