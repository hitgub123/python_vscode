import os
from typing import List
from pydantic import BaseModel
from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.llms.gemini import Gemini
from llama_index.core.prompts import PromptTemplate
import json


# 定义数据模型
class Poem(BaseModel):
    title: str
    author: str
    content: str


# 初始化 LlamaIndex 的 LLM（使用 Gemini）
def get_llm():
    llm = Gemini(
        model_name="models/gemini-1.5-flash",
        api_key=os.getenv("gemini_api_key2"),
    )
    return llm


def get_poems():
    llm = get_llm()

    # 加载唐诗文件
    reader = SimpleDirectoryReader(input_files=["doc/唐诗三百首.txt"])
    documents = reader.load_data()
    text = documents[0].text

    prompt_template = PromptTemplate(
        """
        Extract up to 5 poems from the following Chinese Tang poem text into a JSON array of objects.
        Each object must have:
        - 'title': string (poem's title)
        - 'author': string (poet's name)
        - 'content': string (full poem content, preserve line breaks)

        Skip incomplete or unclear poems. Return an empty array if no poems are found.
        Output as JSON without wrapped in triple backticks (```json\n...\n```).

        Text:
        {text}
        """
    )

    generation_config = {
        "response_mime_type": "application/json",
        "response_schema": list[Poem],
    }

    response = llm.complete(
        prompt_template.format(text=text[:10000]), 
        # generation_config=generation_config
    )

    # 解析 JSON 输出
    print(response.text)
    # poems_data = json.loads(response.text)
    # poems = [Poem(**data) for data in poems_data]
    # print(poems)


if __name__ == "__main__":
    get_poems()
