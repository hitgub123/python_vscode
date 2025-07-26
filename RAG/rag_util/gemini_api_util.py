from google import genai
from google.genai import types
import os, time
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Choose the appropriate import based on your API:
from langchain_google_genai import ChatGoogleGenerativeAI


config = {
    "model": "gemini-2.5-flash",
    "embedding_model": "gemini-embedding-001",
    "temperature": 0,
    "max_tokens": None,
    "top_p": 0.8,
    "google_api_key": os.environ.get("gemini_api_key2"),
}


def get_llm():
    # Initialize with Google AI Studio
    llm = LangchainLLMWrapper(
        ChatGoogleGenerativeAI(
            model=config["model"],
            temperature=config["temperature"],
            max_tokens=config["max_tokens"],
            top_p=config["top_p"],
            google_api_key=config["google_api_key"],
        )
    )
    return llm


def get_embeddings():
    embeddings = LangchainEmbeddingsWrapper(
        GoogleGenerativeAIEmbeddings(
            model=config["embedding_model"],  # Google's text embedding model
            # task_type="retrieval_document",  # Optional: specify the task type
        )
    )
    return embeddings


def get_ai_client():
    api_key = os.environ.get("gemini_api_key2")
    client = genai.Client(api_key=api_key)
    return client


def get_embedings(texts, dims, model=config["embedding_model"], batch_size=100):
    embeddings = []

    client = get_ai_client()
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]  # 每批最多 100 个
        try:
            result = client.models.embed_content(
                model=model,
                contents=batch,
                config=types.EmbedContentConfig(output_dimensionality=dims),
            )
            embeddings.extend(result.embeddings)  # 收集嵌入结果
            print(f"get_embedings : Current : {i // batch_size}")
            time.sleep(60)
        except Exception as e:
            print(f"Error in batch {i // batch_size}: {str(e)}")
    return embeddings

if __name__ == "__main__":
    client=get_ai_client()
    response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="How does AI work?",
    config=types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(thinking_budget=0) # Disables thinking
        ),
    )
    print(response.text)