from http.client import responses

from gradio.themes.builder_app import history
from langgraph.constants import START,END
from langgraph.graph import StateGraph
from langgraph.config import get_stream_writer
from langgraph.types import Command
from pydantic import BaseModel
from ioc import IoCContainer
from prompt_manager import PromptManager
from milvus_retrieval import MilvusHybridRetriever
from llm_client import  OpenAIClient
from loguru import logger
from embedding_client import OpenAIEmbeddingClient
import asyncio
import json
import time
import re
from typing import Any,Dict
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

class QaState(BaseModel):
    target: str
    plan:Dict
    current_step:int
    complete_steps:list
    answer:Dict
    Knowledge:str
    augment:Any
    chunks:list
    result:Any
    error:Any

class Qa_plan:
    async def __call__(self, state: QaState):
        system = IoCContainer.get_instance().resolve("PromptManager").get("plan_rag")
        target = state.target
        messages = [
            {"role":"system","content":system},
            {"role": "user", "content": target}
        ]
        try:
            writer = get_stream_writer()
            response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(messages=messages,stream=True)
            content = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content
                    writer(chunk.choices[0].delta.content)
            plan = parse_json_or_array(content)
            answer = {str(i + 1): "" for i in range(len(plan))}
            return Command(update={"plan": plan,"answer":answer,"current_step":1},goto="Qa_augment")
        except Exception as e:
            exception = str(e)
            return Command(update={"error": f"{exception}"})

class Qa_augment:
    async def __call__(self, state: QaState):
        system = IoCContainer.get_instance().resolve("PromptManager").get("augment")
        prompt = self.build_prompt(state)
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        try:
            writer = get_stream_writer()
            # response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(messages=messages, stream=False)
            response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(messages=messages, stream=True)

            content = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content
                    writer(chunk.choices[0].delta.content)
            augment = parse_json_or_array(content)
            return Command(update={"augment": augment},goto="Qa_retrieval")
        except Exception as e:
            exception = str(e)
            return Command(update={"error": f"{exception}"})

    def build_prompt(self, state: QaState) -> str:
        """
        构建问答上下文，用于增强阶段。
        输出格式示例：

        target: 《西游记》中唐僧的二徒弟是谁？
        Knowledge: 唐僧的徒弟包括孙悟空、猪八戒、沙和尚。
        progress:
        step_1:
            task: "确认唐僧的三个徒弟分别是谁"
            answer: "孙悟空、猪八戒、沙和尚"
        step_2:
            task: "确定三个徒弟的排序"
            answer: "大徒弟孙悟空，二徒弟猪八戒，三徒弟沙和尚"
        """

        current_step=state.current_step
        current_task = ""
        lines = []
        lines.append(f"target: {state.target}")
        lines.append(f"Knowledge: {state.Knowledge or '（暂无知识汇总）'}")
        lines.append("progress:")

        if isinstance(state.plan, dict):
            for i, (step_id, step_desc) in enumerate(state.plan.items(), start=1):
                if i == current_step:
                    current_task = step_desc
                lines.append(f"step_{i}:")
                lines.append(f'  task: "{step_desc}"')
                answer =state.answer.get(str(i)) or "暂未回答"
                lines.append(f'  answer: "{answer}"')
        lines.append(f"current_step: {current_step}")
        lines.append(f'  task: "{current_task}"')
        return "\n".join(lines)
    
    
        
        
class Qa_retrieval:
    async def __call__(self, state: QaState):
        current_step = state.current_step
        if current_step==1:
        # response = await IoCContainer.get_instance().resolve("MilvusHybridRetriever").bm25_search(collection_name="documents",query=augment)
            response = ["苹果的股价是1000","谷歌的股价是9000"]
        else:
            response = []
        return Command(update={"chunks": response},goto="Qa_answer")
#
class Qa_answer:
    async def __call__(self, state: QaState):
        current_step = state.current_step
        system = IoCContainer.get_instance().resolve("PromptManager").get("answer_rag")
        prompt = self.build_prompt(state)
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        try:
            writer = get_stream_writer()
            response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(messages=messages,
                                                                                            stream=True)
            content = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content
                    writer(chunk.choices[0].delta.content)
            result = parse_json_or_array(content)
            CanAnswerTarget = result.get("CanAnswerTarget")
            if CanAnswerTarget:
                TargetAnswer = result.get("TargetAnswer")
                return Command(update={"result": TargetAnswer}, goto="Qa_finish")
            # else:
            #     CompletedSteps = sorted([int(x) for x in result.get("CompletedSteps") if str(x).isdigit()])
            #     if CompletedSteps == current_step:
        except Exception as e:
            exception = str(e)
            return Command(update={"error": f"{exception}"})

    def build_prompt(self, state: QaState) -> str:
        """
        构建问答上下文（严格按照以下顺序）：
        1. Target
        2. Plan (全局任务规划)
        3. Progress (已完成步骤及回答)
        4. Knowledge (知识汇总)
        5. Retrieved chunks (当前检索到的信息)
        6. Current step (当前待回答任务)
        """

        lines = []

        # 1️⃣ Target
        lines.append(f"Target: {state.target}")

        # 2️⃣ Plan
        lines.append("Plan:")
        if isinstance(state.plan, dict) and len(state.plan) > 0:
            for step_id, step_desc in state.plan.items():
                lines.append(f'  {step_id}. {step_desc}')
        else:
            lines.append("no plan available")

        # 3️⃣ Progress
        lines.append("Progress:")
        if hasattr(state, "answer") and isinstance(state.answer, dict) and len(state.answer) > 0:
            for i, (step_id, step_desc) in enumerate(state.plan.items(), start=1):
                answer = state.answer.get(str(i)) if state.answer.get(str(i)) != "" else "no answer yet"
                lines.append(f"  Step_{i}:")
                lines.append(f'    task: "{step_desc}"')
                lines.append(f'    answer: "{answer}"')
        else:
            lines.append("no progress yet")

        # 4️⃣ Knowledge
        lines.append(f"Knowledge: {state.Knowledge or 'no knowledge available'}")

        # 5️⃣ Retrieved chunks
        if hasattr(state, "chunks") and state.chunks:
            lines.append("Retrieved Chunks From Knowledge Base:")
            for idx, chunk in enumerate(state.chunks, start=1):
                lines.append(f"chunk_{idx}: {chunk}.")
        else:
            lines.append("Retrieved Chunks:no chunks available")

        # 6️⃣ Current step
        current_step = state.current_step
        current_task = ""
        if isinstance(state.plan, dict) and str(current_step) in state.plan:
            current_task = state.plan[str(current_step)]
        lines.append(f"Current Step: {current_step}")
        lines.append(f'  task: "{current_task}"')

        return "\n".join(lines)

#
class Qa_replan:
    async def __call__(self, state: QaState):
        current_step=state.current_step
        system = IoCContainer.get_instance().resolve("PromptManager").get("replan")
        prompt = self.build_prompt(state)
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ]
        try:
            writer = get_stream_writer()
            response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(messages=messages, stream=True)
            content = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content
                    writer(chunk.choices[0].delta.content)
            result = parse_json_or_array(content)
            replan_required = bool(result.get("replan_required", False))
            new_plan = result.get("new_plan", {})
            if replan_required:
                return Command(update={"plan": new_plan,"current_step":1},goto="Qa_augment")
            else:
                return Command(update={},goto="Qa_retrieval")
     
        except Exception as e:
            exception = str(e)
            return Command(update={"error": f"{exception}"})

    def build_prompt(self, state: QaState) -> str:
        """
        构建验证上下文（严格按照以下顺序）：
        1. Target
        2. Plan (全局任务规划)
        3. Progress (已完成步骤及回答)
        4. Knowledge (知识汇总)
        5. The current sub_task and its corresponding answer that need to be validated
        """

        lines = []

        # 1️⃣ Target
        lines.append(f"Target: {state.target}")

        # 2️⃣ Plan
        lines.append("Plan:")
        if isinstance(state.plan, dict) and len(state.plan) > 0:
            for step_id, step_desc in state.plan.items():
                lines.append(f"  {step_id}. {step_desc}")
        else:
            lines.append("  no plan available")

        # 3️⃣ Progress
        lines.append("Progress:")
        if hasattr(state, "answer") and isinstance(state.answer, dict) and len(state.answer) > 0:
            for i, (step_id, step_desc) in enumerate(state.plan.items(), start=1):
                answer = state.answer.get(str(i)) or "no answer yet"
                lines.append(f"  Step_{i}:")
                lines.append(f'    task: "{step_desc}"')
                lines.append(f'    answer: "{answer}"')
        else:
            lines.append("  no progress yet")

        # 4️⃣ Knowledge
        lines.append(f"Knowledge: {state.Knowledge or 'no knowledge available'}")

        # 5️⃣ 当前待验证的 sub_task 和其 answer
        if hasattr(state, "current_step") and state.current_step is not None:
            step_id = str(state.current_step-1)
            sub_task = state.plan.get(step_id, "unknown sub_task")
            sub_answer = state.answer.get(step_id, "no answer yet")
            lines.append("\nThe current sub_task and its corresponding answer that need to be validated:")
            lines.append(f"  Step_{step_id}")
            lines.append(f'  task: "{sub_task}"')
            lines.append(f'  answer: "{sub_answer or "no answer yet"}"')
        else:
            lines.append("\nThe current sub_task and its corresponding answer that need to be validated: not specified")

        return "\n".join(lines)

class Qa_finish:
    async def __call__(self, state: QaState):
      pass
def build_graph():
    graph_builder = StateGraph(QaState)
    Qa_plan_node = Qa_plan()
    Qa_augment_node =Qa_augment()
    Qa_retrieval_node = Qa_retrieval()
    Qa_answer_node = Qa_answer()
    Qa_replan_node = Qa_replan()
    Qa_finish_node= Qa_finish()
    graph_builder.add_node("Qa_plan",Qa_plan_node)
    graph_builder.add_node("Qa_augment",Qa_augment_node)
    graph_builder.add_node("Qa_retrieval",Qa_retrieval_node)
    graph_builder.add_node("Qa_answer",Qa_answer_node)
    graph_builder.add_node("Qa_replan",Qa_replan_node)  
    graph_builder.add_node("Qa_finish",Qa_finish_node)

    graph_builder.add_edge(START, "Qa_plan")
    graph_builder.add_edge("Qa_finish", END)


    graph = graph_builder.compile()
    return graph

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

    # container.register_class(
    #     key="MilvusHybridRetriever",
    #     cls=MilvusHybridRetriever,
    #     singleton=True,
    #     constructor_kwargs={"url": "http://10.60.200.100:19530","token":"root:Milvus"}
    # )
    container.initialize_all_singletons()
    graph = build_graph()
    # x = graph.get_graph().draw_mermaid_png()
    # with open("graph.png", "wb") as f:
    #     f.write(x)  
    # print("Graph built and saved as graph.png")
    async def main():
        try:
            async for chunk in graph.astream({
                "target": "帮我看一下今年天合富家的经验情况",
                "plan": {},
                "answer": {},
                "current_step": 0,
                "complete_steps":[],
                "Knowledge": "",
                "augment": "",
                "chunks":[],
                "result":"",
                "error": ""
            }, stream_mode="custom"):
                token_str = chunk
                print(token_str, end="", flush=True)
                # for char in token_str:
                #     print(char,end="",flush=True)
        except Exception as e:
            print(f"❌ 出错：{e}")
#         text ='''
# step_1:
#     sub_task: "确认《西游记》中唐僧的三个徒弟分别是谁",
#     answer: "孙悟空，猪八戒"
# step_2:
#     sub_task: "确定三个徒弟的排序：大徒弟、二徒弟",
#     answer: ""
# step_3:
#     sub_task: "根据排序找出唐僧的二徒弟是谁",
#     answer: ""
# 判断step_2中answer是否可以从逻辑上回复sub_task。
#         '''
        text_au ='''
target: "西游记中唐僧的二徒弟是谁"
Plan progress:
    step_1:
        task: "确认《西游记》中唐僧的三个徒弟分别是谁",
        answer: "孙悟空，猪八戒和沙僧"
    step_2:
        task: "确定三个徒弟的排序：大徒弟、二徒弟",
        answer: "no answer yet"
    step_3:
        task: "根据排序找出唐僧的二徒弟是谁",
        answer: "no answer yet"
'''
        system = IoCContainer.get_instance().resolve("PromptManager").get("new_replan_logic")
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": text_au}]
        response = await IoCContainer.get_instance().resolve("OpenAIClient").call_async(
            messages=messages,
            stream=False,
            # response_format={'type': 'json_object'}
        )
        print(response.choices[0].message.content)
        print(parse_json_or_array(response.choices[0].message.content))
#
#         # print(extract_json_brace_block(response.choices[0].message.content))
#         # while True:
#         #     # user_input = input("请输入内容：").strip()
#         #     # if not user_input:
#         #     #     continue
#         #     # print("⏳ 正在处理...")
#         #     # start = time.time()
#         #
#         #     # end = time.time()
#         #     # print(f"⏱️ 本轮耗时：{end - start:.2f} 秒")

    asyncio.run(main())
