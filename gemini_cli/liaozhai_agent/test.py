import os
import torch
from typing import Any, Iterator, List
from pydantic import Field, ConfigDict  # Pydantic v2
from dotenv import load_dotenv

# LangChain 相关的导入
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
from langchain_core.outputs import ChatResult, Generation

# LangGraph 相关的导入
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

# Hugging Face 相关的导入
from transformers import AutoTokenizer, AutoModelForCausalLM


# --- 1. 定义 LocalLLM 类 (与之前提供的相同，确保它在您的代码中可用) ---
class LocalLLM(BaseChatModel):
    """
    一个用于本地运行 Hugging Face LLM 的 LangChain ChatModel 封装器。
    它加载 Hugging Face 的 tokenizer 和 causal language model。
    """

    # llm_name: str
    # tokenizer: Any  # 使用 Any 允许复杂对象
    # model_instance: Any  # 使用 Any 允许复杂对象

    # model_config = ConfigDict(arbitrary_types_allowed=True)  # 允许任意类型
    llm_name: str = Field(default="google/gemma-3-1b-it")
    tokenizer: AutoTokenizer = None
    model_instance: AutoModelForCausalLM = None
    # tools: list = None    

    def __init__(self, llm_name: str = "google/gemma-3-1b-it", **kwargs: Any):
        super().__init__(llm_name=llm_name, **kwargs)

        # 确保 Hugging Face Token (如果模型是 gated 的)
        # 例如 Llama 3/3.2 模型需要登录或设置 HF_TOKEN
        # os.environ["HF_TOKEN"] = "hf_YOUR_TOKEN_HERE" # 如果需要手动设置

        self.tokenizer = AutoTokenizer.from_pretrained(self.llm_name)

        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading model '{self.llm_name}' on device: {device}")

        # 如果是 Llama 3.2, 确保您已接受 Hugging Face 的条款并登录 CLI
        # 对于较大型号可能需要 load_in_8bit/4bit 和 bitsandbytes
        self.model_instance = AutoModelForCausalLM.from_pretrained(
            self.llm_name,
            torch_dtype=(
                torch.bfloat16
                if device == "cuda" and torch.cuda.is_available()
                else torch.float32
            ),
            device_map=device,
            # load_in_8bit=True # 示例：如果内存不足，可以尝试量化
        )
        self.model_instance.eval()  # 设置为评估模式
        print("Model loaded successfully.")

    def _generate(self, messages: List[BaseMessage], **kwargs: Any) -> ChatResult:
        formatted_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted_messages.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted_messages.append({"role": "model", "content": msg.content})
            elif isinstance(msg, SystemMessage):
                formatted_messages.insert(0, {"role": "system", "content": msg.content})

        # 将输入移动到模型所在的设备
        input_ids = self.tokenizer.apply_chat_template(
            formatted_messages, add_generation_prompt=True, return_tensors="pt"
        ).to(self.model_instance.device)

        # 合并生成参数
        generate_params = {
            "max_new_tokens": kwargs.get("max_new_tokens", 200),
            "temperature": kwargs.get("temperature", 0.7),
            "do_sample": kwargs.get("temperature", 0.7)
            > 0,  # 如果温度大于0，则进行采样
            "top_k": kwargs.get("top_k", 50),
            "top_p": kwargs.get("top_p", 0.95),
            "pad_token_id": self.tokenizer.eos_token_id,  # 确保生成停止
        }
        # 确保 do_sample=False 时 temperature 不为 0.0
        if not generate_params["do_sample"]:
            generate_params["temperature"] = 1.0  # 当不采样时，温度值不再重要，设为非零

        outputs = self.model_instance.generate(input_ids, **generate_params)

        response_text = self.tokenizer.decode(
            outputs[0][input_ids.shape[1] :], skip_special_tokens=True
        )

        generation = Generation(text=response_text)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "local_huggingface_llm"

    # def _stream(self, messages: List[BaseMessage], **kwargs: Any) -> Any:
    #     raise NotImplementedError("Streaming is not yet implemented for LocalLLM.")
    def _stream(
        self,
        messages: List[BaseMessage],
        **kwargs: Any,
    ) -> Iterator[ChatResult]:
        """Implement streaming, yielding one chunk at a time."""
        # 实际流式实现会更复杂，这里是简单模拟
        full_result = self._generate(messages, **kwargs)
        # Yield the entire result as one chunk.
        # For true streaming, you'd yield token by token.
        yield full_result    

    def _get_token_ids(self, text: str) -> List[int]:
        return self.tokenizer.encode(text, add_special_tokens=False)


# --- 2. 设置环境变量和工具 ---
load_dotenv()  # 加载 .env 文件中的 HF_TOKEN (如果需要)


@tool
def get_weather(city: str) -> str:
    """Gets the current weather for a specific city."""
    if "san francisco" in city.lower() or "sf" in city.lower():
        return "The weather in San Francisco is 20°C and sunny."
    elif "tokyo" in city.lower():
        return "The weather in Tokyo is 28°C and humid with occasional rain."
    else:
        return f"I don't have weather information for {city} at the moment."


# --- 3. 实例化 LocalLLM 模型 ---
# 选择您要使用的 Hugging Face 模型。
# 例如，如果您想用 Llama 3.2 1B (确保已接受条款并登录 HF CLI)
# model_name_for_agent = "meta-llama/Llama-3.2-1B"
# 或者 Gemma 3.1 1B (推荐，因为您之前提到了它)
model_name_for_agent = "google/gemma-3-1b-it"

print(f"Initializing LocalLLM with: {model_name_for_agent}")
local_llm_model = LocalLLM(llm_name=model_name_for_agent)


# --- 4. 创建 LangGraph Agent ---
# 将您的 LocalLLM 实例作为 llm 参数传递
agent = create_react_agent(
    model=local_llm_model,  # <--- 将 LocalLLM 实例传递到这里
    tools=[get_weather],
    prompt="You are a helpful AI assistant that can answer questions and use tools.",
)

# --- 5. 运行 Agent ---
# 运行 Agent Executor (create_react_agent 返回的是一个 Runnable)
try:
    print("\nRunning the agent...")
    response = agent.invoke(
        {"messages": [HumanMessage(content="What's the weather like in Tokyo?")]}
    )

    print("\n--- Agent Execution Complete ---")
    # agent.invoke 返回的通常是一个字典，其中 'messages' 键包含完整的消息历史
    # 最后一个消息是 AI 的最终回答
    if isinstance(response, dict) and "messages" in response:
        print("Final AI Message:")
        print(response["messages"][-1].content)
    else:
        print("Unexpected response format:", response)

except Exception as e:
    print(f"\nAn error occurred during agent execution: {e}")
    print("\nPossible reasons:")
    print(
        "1. Hugging Face model download/authentication issue (e.g., HF_TOKEN, model terms)."
    )
    print("2. Insufficient VRAM/RAM for the model.")
    print("3. Errors within the _generate method (check chat template, tokenization).")
