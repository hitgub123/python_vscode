from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langsmith import Client
import os, sys

sys.path.extend(
    [os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "rag_util"))]
)
from model import model_util


llm = model_util.get_model()

client = Client()

prompt = ChatPromptTemplate.from_template("回答问题：{question}")
chain = prompt | llm

response = chain.invoke({"question": "什么是 RAG？"}, config={"tags": ["example-run"]})
print(response.content)