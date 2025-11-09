from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.config import get_stream_writer
from langgraph.types import Command
from typing import TypedDict, Any
from pydantic import BaseModel
from ioc import IoCContainer
from prompt_manager import PromptManager
from llm_client import  OpenAIClient
from loguru import logger
from embedding_client import OpenAIEmbeddingClient
import asyncio
import json
import time
class QaState(BaseModel):
    target: str
    node: Any
    plan:Any
    function_name: str
    function_args: Any
    result:Any
    error:Any


import json
import re
from typing import Any


def parse_json_or_array(text: str) -> Any:
    """
    从字符串中提取并解析 JSON 对象或数组。
    - 自动识别是单个对象还是数组
    - 自动修剪多余文本
    - 自动跳过前后杂质字符
    - 若解析失败则返回 None

    示例：
        parse_json_or_array('{"a":1}')           -> {'a': 1}
        parse_json_or_array('[{"a":1},{"b":2}]') -> [{'a':1}, {'b':2}]
        parse_json_or_array('前缀 [{"x":2}] 后缀') -> [{'x':2}]
    """

    # 1️⃣ 提取第一个 JSON 对象或数组（最外层匹配）
    pattern = r'(\{.*\}|\[.*\])'
    match = re.search(pattern, text.strip(), re.DOTALL)
    if not match:
        return None

    json_str = match.group(1)

    # 2️⃣ 尝试解析
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        # 尝试修复常见格式错误
        fixed = (
            json_str
            .replace("'", '"')       # 单引号→双引号
            .replace("None", "null") # Python None → JSON null
            .replace("True", "true")
            .replace("False", "false")
            .strip()
        )
        try:
            return json.loads(fixed)
        except Exception:
            return None


async def plan(self, state: QaState) -> Command:
    """LangGraph 标准入口"""
    try:
        logger.info(f"➡️ Running node: plan")
        system = IoCContainer.get_instance().resolve("PromptManager").get("plan")
        target = state.target
        messages = [{"role":"system","content":system},{"role": "user", "content": f"{target}"}]
        response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(messages=messages, stream=False)
        content = response.choices[0].content
        arguments = json.loads(arguments)

        update = await self.run(state)
        goto = update.pop("goto", self.next_step)
        logger.info(f"✅ Node {self.name} completed, next: {goto}")
        return Command(update=update, goto=goto)
    except Exception as e:
        logger.exception(f"❌ Error in node {self.name}: {e}")
        return Command(update={"error": str(e)}, goto="agent_finish")

async def augment(self, state: QaState) -> Command:
    """LangGraph 标准入口"""
    try:
        logger.info(f"➡️ Running node: augment")
        system = IoCContainer.get_instance().resolve("PromptManager").get("augment")


        target = state.target
        plan = state.plan
        prompt = f'''
        target:{target}
        
        '''


        messages = [{"role":"system","content":system},{"role": "user", "content":"" }]
        response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(messages=messages, stream=False)
        content = response.choices[0].content
        arguments = json.loads(arguments)

        update = await self.run(state)
        goto = update.pop("goto", self.next_step)
        logger.info(f"✅ Node {self.name} completed, next: {goto}")
        return Command(update=update, goto=goto)
    except Exception as e:
        logger.exception(f"❌ Error in node {self.name}: {e}")
        return Command(update={"error": str(e)}, goto="agent_finish")


#

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
        constructor_kwargs={"prompt_dir": r"E:\robot\prompts"}
    )

    container.initialize_all_singletons()


    #
    # graph = build_graph()
    #

    async def main():

        text ='''
step_1:
    sub_task: "确认《西游记》中唐僧的三个徒弟分别是谁",
    answer: "孙悟空，猪八戒"
step_2:
    sub_task: "确定三个徒弟的排序：大徒弟、二徒弟",
    answer: ""  
step_3:
    sub_task: "根据排序找出唐僧的二徒弟是谁",
    answer: ""
判断step_2中answer是否可以从逻辑上回复sub_task。
        '''
        text_au ='''
target: "西游记中唐僧的二徒弟是谁"
Plan progress: 
    step_1:
        task: "确认《西游记》中唐僧的三个徒弟分别是谁",
        answer: "孙悟空，猪八戒，沙和尚"
    step_2:
        task: "确定三个徒弟的排序：大徒弟、二徒弟",
        answer: ""  
    step_3:
        task: "根据排序找出唐僧的二徒弟是谁",
        answer: ""
Existing knowledge: “”
Current task: 确定三个徒弟的排序：大徒弟、二徒弟
'''


        system = IoCContainer.get_instance().resolve("PromptManager").get("augment")
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": text_au}]
        response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(
            messages=messages,
            stream=False,
            # response_format={'type': 'json_object'}
        )
        # print(response.choices[0].content)
        print(parse_json_or_array(response.choices[0].message.content))

        # print(extract_json_brace_block(response.choices[0].message.content))

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
