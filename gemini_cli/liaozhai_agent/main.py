

# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv
from typing import TypedDict, Annotated, Sequence
import operator

from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from stories import LIAOZHAI_STORIES

# --- LLMとツールの定義 ---

# LLMを初期化。ツールとエージェントの両方からアクセスできるようにします。
# Geminiはシステムメッセージをサポートしないため、人間とモデルの対話形式に変換します。
llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)

@tool
def get_story_data(story_title: str) -> str:
    """根据故事标题，获取《聊斋志异》的原文和现代文译文。
    (Get the original and modern Chinese text of a Liaozhai story based on its title.)"""
    print(f"\n--- TOOL CALL: get_story_data(story_title='{story_title}') ---")
    story = LIAOZHAI_STORIES.get(story_title)
    if story:
        return f"已找到《{story_title}》\n原文: {story['original']}\n现代文: {story['modern']}"
    else:
        return f"错误：未找到名为《{story_title}》的故事。"

# 潤色ツールの入力スキーマを定義して、より明確にします
class PolishStorySchema(BaseModel):
    story_title: str = Field(description="需要润色的小说标题 (The title of the story to be polished)")
    user_request: str = Field(description="用户的具体润色要求 (The user's specific request for polishing)")

@tool(args_schema=PolishStorySchema)
def polish_and_rewrite_story(story_title: str, user_request: str) -> str:
    """根据用户的具体要求，对指定的故事进行文学性的润色和改写。
    (Polishes and rewrites a specific story based on the user's request.)"""
    print(f"\n--- TOOL CALL: polish_and_rewrite_story(story_title='{story_title}', user_request='{user_request}') ---")
    
    # まず物語のデータを取得します
    story_data = get_story_data.invoke({"story_title": story_title})
    if "错误" in story_data:
        return story_data

    # ツール内で潤色用のチェーンを定義します
    polish_prompt = PromptTemplate(
        template="""你是一位文笔卓越的小说家。请根据以下的原始材料以及用户的具体要求，对故事进行文学性的润色和改写。

**核心任务**: 在保留原始情节和人物核心特质的前提下，通过丰富的描写、细腻的心理刻画和生动的语言，使故事更具感染力。

**约束条件**:
1.  **忠于原作**: 不得改变故事的基本情节、人物关系和结局。
2.  **深化描写**: 强化场景、外貌、神态、动作和环境的描写，营造身临其境的氛围。
3.  **文字优美**: 使用流畅、优雅且富有表现力的现代汉语进行创作。

---
**原始材料**:
{story_data}

**用户的具体要求**:
{user_request}

---
请开始你的创作：""",
        input_variables=["story_data", "user_request"]
    )
    
    # 新しい構文: prompt | llm | parser
    polish_chain = polish_prompt | llm | StrOutputParser()
    
    # チェーンを実行します
    result = polish_chain.invoke({
        "story_data": story_data,
        "user_request": user_request
    })
    return result

# --- エージェントの状態とグラフの定義 ---

tools = [get_story_data, polish_and_rewrite_story]
# ToolNodeは、ツールを実行するための標準的な方法です
tool_node = ToolNode(tools)

# LLMにツールをバインドして、いつツールを呼び出すべきかをモデルに知らせます
model = llm.bind_tools(tools)

# エージェントの状態を定義します。メッセージのリストを保持します。
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# グラフのノードを定義します

def should_continue(state: AgentState) -> str:
    """プロセスを続行するか終了するかを決定します。"""
    last_message = state['messages'][-1]
    # ツール呼び出しがなければ終了します
    if not last_message.tool_calls:
        return "end"
    # ツール呼び出しがあれば続行します
    return "continue"

def call_model(state: AgentState) -> dict:
    """LLMを呼び出して次のアクションを決定します。"""
    messages = state['messages']
    response = model.invoke(messages)
    # 新しいメッセージをリストとして返し、既存のリストに追加します
    return {"messages": [response]}

# グラフのワークフローを定義します
workflow = StateGraph(AgentState)

# ノードを追加します
workflow.add_node("agent", call_model)
workflow.add_node("action", tool_node)

# エントリーポイントを設定します
workflow.set_entry_point("agent")

# 条件付きエッジを追加します
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "action",
        "end": END
    }
)

# actionからagentへの通常のエッジを追加します
workflow.add_edge('action', 'agent')

# グラフをコンパイルして実行可能なアプリケーションを作成します
app = workflow.compile()

# --- メインの実行部分 ---

def main():
    load_dotenv()
    if os.getenv("GOOGLE_API_KEY") is None:
        print("错误: 环境变量 'GOOGLE_API_KEY' 未设置。")
        print('请在 .env 文件中设置您的API密钥，格式为 \'GOOGLE_API_KEY="YOUR_API_KEY_HERE"\'')
        return

    user_query = "我想让《画皮》这个故事的文笔更优美，更有诗意。你能帮我改写一下吗？"
    print(f"--- 用户查询 ---\n{user_query}\n")

    # エージェントを実行します
    inputs = {"messages": [HumanMessage(content=user_query)]}
    
    print("--- Agent 开始思考... ---")
    # streamメソッドを使うと、エージェントの各ステップの出力をリアルタイムで確認できます
    for output in app.stream(inputs, {"recursion_limit": 10}):
        for key, value in output.items():
            print(f"--- 来自节点: {key} ---")
            # メッセージの内容を整形して表示
            if 'messages' in value:
                for msg in value['messages']:
                    if msg.tool_calls:
                        print(f"  - Tool Call: {msg.tool_calls}")
                    else:
                        print(f"  - AI: {msg.content}")
            else:
                 print(value)
        print("\n--------------------------------\n")

    # 最終的な状態を取得します
    final_state = app.invoke(inputs, {"recursion_limit": 10})
    final_answer = final_state['messages'][-1].content

    print("--- Agent执行完毕 ---")
    print("--- 最终结果 ---")
    print(final_answer)

if __name__ == "__main__":
    main()
