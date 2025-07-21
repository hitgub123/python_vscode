from langchain_community.embeddings import OllamaEmbeddings

# 确保 Ollama 服务在后台运行
embeddings = OllamaEmbeddings(model="nomic-embed-text", base_url="http://localhost:11434")

# 生成一个短句的嵌入
text_short = "Hello, world!"
embedding_short = embeddings.embed_query(text_short)
print(f"短句嵌入维度: {len(embedding_short)}")

# 尝试生成一个长文本的嵌入
text_long = " ".join(["This is a test sentence for long context embedding."] * 100) # 生成一个较长的文本
embedding_long = embeddings.embed_query(text_long)
print(f"长句嵌入维度: {len(embedding_long)}")
print("长句嵌入已生成。")