import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
import os, sys
from langsmith import Client

os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
client = Client()
device = "cuda" if torch.cuda.is_available() else "cpu"
# model_name = "meta-llama/Llama-3.2-3B-Instruct can not use"
# model_name = "microsoft/bitnet-b1.58-2B-4T can not use"
# model_name = "meta-llama/Llama-3.2-1B-Instruct"
model_name = "google/gemma-3-1b-it"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.eval()
messages = [
    {"role": "system", "content": "You are a factual AI assistant. Provide direct, concise answers to questions without additional commentary or questions."},
    {"role": "user", "content": "What is the capital of France?who is the president of USA?"},
]
inputs = tokenizer.apply_chat_template(
    messages,
    load_in_1bit=True,
    add_generation_prompt=True,
    tokenize=True,
    return_dict=True,
    return_tensors="pt",
).to(device)

outputs = model.generate(
    **inputs,
    max_new_tokens=256,
    temperature=0.7,
)
response = tokenizer.decode(
    outputs[0][inputs["input_ids"].shape[-1] :], skip_special_tokens=True
)
