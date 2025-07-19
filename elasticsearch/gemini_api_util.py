from google import genai
from google.genai import types
import os, time


def get_ai_client():
    api_key = os.environ.get("gemini_api_key2")
    client = genai.Client(api_key=api_key)
    return client


def get_embedings(texts, dims, model="gemini-embedding-001", batch_size=100):
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
