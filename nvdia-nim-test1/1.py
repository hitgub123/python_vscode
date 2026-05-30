from openai import OpenAI
import os, time


api_key = os.environ.get("nvidia-api-key-key1")
client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = api_key
)

while 1:
  content= input('\n请输入提示词\n')
  completion = client.chat.completions.create(
    model="deepseek-ai/deepseek-v4-flash",
    # model="deepseek-ai/deepseek-v4-pro",
    messages=[{"role":"user","content":content}],
    temperature=1,
    top_p=0.95,
    max_tokens=16384,
    extra_body={"chat_template_kwargs":{"thinking":False}},
    stream=True
  )

  for chunk in completion:
    if not getattr(chunk, "choices", None):
      continue
    if chunk.choices and chunk.choices[0].delta.content is not None:
      print(chunk.choices[0].delta.content, end="")
    
  print(r'\n','='*111,r'\n')
