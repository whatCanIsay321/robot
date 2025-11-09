from typing import Annotated
from operator import add
from typing_extensions import TypedDict
import random
from typing_extensions import TypedDict, Literal

from langgraph.graph import StateGraph, START
from langgraph.types import Command


# 图态定义：图态是一种量子态，其描述通过图论中的图来表示。在量子信息中，图态通常与多体量子系统相关联，其中每个节点代表一个量子比特，而边表示节点之间的纠缠关系。图态能够用于多种量子计算和量子通信任务，特别是在量子网络和量子态传输中具有重要应用。


def dedupe_concat(old: list[int], new: list[int]) -> list[int]:
    res = old[:]
    for x in new:
        if x not in res:
            res.append(x)
    return [111111]

class State(TypedDict):
    foo: Annotated[list[int], dedupe_concat]

# 定义节点


def node_a(state: State) -> Command[Literal["node_b", "node_c"]]:
    print("Called A")
    value = random.choice(["a", "b"])
    # 这是一个条件边函数的替代方案。
    if value == "a":
        goto = "node_b"
    else:
        goto = "node_c"

    # 请注意，Command 允许您既更新图形状态又路由到下一个节点。
    return Command(
        # 这是状态更新。
        update={"foo": value},
        # 这是边缘的替代品。
        goto=goto,
    )


# 节点B和C没有变化。


def node_b(state: State):
    print("Called B")
    return {"foo": state["foo"] + ["b"]}


def node_c(state: State):
    print("Called C")
    return {"foo": state["foo"] + ["c"]}

builder = StateGraph(State)
builder.add_edge(START, "node_a")
builder.add_node(node_a)
builder.add_node(node_b)
builder.add_node(node_c)
# 注意：节点 A、B 和 C 之间没有边！

graph = builder.compile()

print(graph.invoke({"foo": [1]}))