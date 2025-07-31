import torch
import os, sys
# do not support amd
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

from unsloth import FastLanguageModel
import torch

device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = ("unsloth/Llama-3.2-3B-Instruct-bnb-4bit",)
# model_name = ("unsloth/Llama-3.2-1B-Instruct-bnb-4bit",)
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=model_name, max_seq_length=512, load_in_4bit=True, device_map=device
)
FastLanguageModel.for_inference(model)
inputs = tokenizer(
    "根据上下文：鸣人的老师是自来也。回答：鸣人的老师是谁？", return_tensors="pt"
).to("cpu")
outputs = model.generate(**inputs, max_length=50)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
