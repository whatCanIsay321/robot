from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.config import get_stream_writer
from langgraph.types import Command
from typing import TypedDict, Any
from ioc import IoCContainer
from prompt_manager import PromptManager
from llm_client import  OpenAIClient
from embedding_client import OpenAIEmbeddingClient
import asyncio
import json
import time


def extract_json_brace_block(text):
    """
    从文本中提取第一个 `{` 到最后一个 `}` 之间的内容（包含括号）。
    适用于提取包裹在大括号中的 JSON 块，允许中间嵌套内容。

    参数:
        text (str): 输入的原始字符串
    返回:
        str | None: 匹配的 JSON 字符串（含大括号），失败则返回 None
    """
    start = text.find('{')
    end = text.rfind('}')
    if start != -1 and end != -1 and start < end:
        return text[start:end + 1]
    return None


#
# class QaState(TypedDict):
#     user_input: str
#     node: Any
#     plan:Any
#     function_name: str
#     function_args: Any
#     result:Any
#     error:Any
#
#
#
#
#
#
# class Qa_plan:
#     async def __call__(self, state: QaState):
#         arguments=""
#         user_input = state.get("user_input")
#         messages = [
#             {"role":"system","content":""},
#             {"role": "user", "content": f"{user_input}"} ]
#
#         try:
#             writer = get_stream_writer()
#             response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(messages=messages,stream=False)
#             content = response.choices[0].content
#             arguments = json.loads(arguments)
#
#             return Command(update={"plan": arguments},
#                                goto='agent_execute')
#         except Exception as e:
#             exception = str(e)
#             return Command(update={"error": f"{exception}"}, goto='agent_finish')
#
#
# class Qa_retrieval:
#     async def __call__(self, state: QaState):
#         arguments=""
#         user_input = state.get("user_input")
#         messages = [
#             {"role":"system","content":""},
#             {"role": "user", "content": f"{user_input}"} ]
#
#         try:
#             writer = get_stream_writer()
#             response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(messages=messages,stream=False)
#             content = response.choices[0].content
#             arguments = json.loads(arguments)
#
#             return Command(update={"function_name": function_name, "function_args": arguments},
#                                goto='agent_execute')
#         except Exception as e:
#             exception = str(e)
#             return Command(update={"error": f"{exception}"}, goto='agent_finish')
#
# class Qa_finish:
#     async def __call__(self, state: QaState):
#         pass
#
# def build_graph():
#     graph_builder = StateGraph(QaState)
#     Qa_plan_node = Qa_plan()
#     Qa_retrieval_node = Qa_retrieval()
#     Qa_finish_node= Qa_finish()
#     graph_builder.add_node("Qa_plan",Qa_plan_node)
#     graph_builder.add_node("Qa_retrieval",Qa_retrieval_node)
#     graph_builder.add_node("Qa_finish",Qa_finish_node)
#
#     graph_builder.add_edge(START, "Qa_plan")
#     graph_builder.add_edge("agent_finish", END)
#
#
#     graph = graph_builder.compile()
#     return graph





if __name__ == "__main__":


    container = IoCContainer.get_instance()

    container.register_class(
        key="OpenAIClient",
        cls=OpenAIClient,
        singleton=True,
        constructor_kwargs={
            "api_key": "sk-dcb3caa7963645669e3205cae1f39464",
            "base_url": "https://api.deepseek.com",
            "model": "deepseek-chat"
        }
    )
    container.register_class(
        key="PromptManager",
        cls=PromptManager,
        singleton=True,
        constructor_kwargs={"prompt_dir": r"D:\PycharmProjects\robot\prompts"}
    )

    container.initialize_all_singletons()


    #
    # graph = build_graph()
    #

    async def main():


        system = IoCContainer.get_instance().resolve("PromptManager").get("plan")
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": " 组件板上为什么有色差？"}]
        response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(messages=messages,stream=False)
        print(extract_json_brace_block(response.choices[0].message.content))

        # while True:
        #     user_input = input("请输入内容：").strip()
        #     if not user_input:
        #         continue
        #     print("⏳ 正在处理...")
        #     start = time.time()
        #     try:
        #         async for chunk in graph.astream({
        #             "user_input": user_input,
        #             "node": container.resolve("tree"),
        #             "function_name": "",
        #             "function_args": "",
        #             "result": "",
        #             "error": ""
        #         },stream_mode="custom"):
        #             token_str = chunk
        #             print(token_str, end="", flush=True)
        #             # for char in token_str:
        #             #     print(char,end="",flush=True)
        #
        #     except Exception as e:
        #         print(f"❌ 出错：{e}")
        #     end = time.time()
        #     print(f"⏱️ 本轮耗时：{end - start:.2f} 秒")

    asyncio.run(main())
