from google import genai
from google.genai import types
import os


def get_ai_client():
    api_key = os.environ.get("ceria_gemini_api_key")
    client = genai.Client(api_key=api_key)
    return client


def get_embedings(text, dims, model="gemini-embedding-001"):
    # text = "Yellowstone National Park"

    # 生成嵌入（截断到 3 维以匹配你的索引）
    result = get_ai_client().models.embed_content(
        model=model,
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=dims),
    )
    emb=result.embeddings
    # print(emb)  # 示例输出: [0.123, -0.456, 0.789]
    return emb
