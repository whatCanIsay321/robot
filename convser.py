import json
import copy

class Conversation:
    def __init__(self, system_prompt="", tools=""):
        self.system_prompt = system_prompt
        self.tools = tools
        self.conversations = []
    def clone(self):
        return copy.deepcopy(self)
    def add(self, role, value, content=None):
        if role == "human":
            self.conversations.append({"from": "human", "value": value})
        elif role == "gpt":
            self.conversations.append({"from": "gpt", "value": value})
        elif role == "observation":
            self.conversations.append({"from": "observation", "value": json.dumps(value, ensure_ascii=False)})
        else:
            raise ValueError("unknown role")
    def export(self):
        return {
            "system_prompt": self.system_prompt,
            "tools": self.tools,
            "conversations": self.conversations
        }

def process_function(conversation, tokenizer, num=1, max_length=2048):
    system_value = conversation["system_prompt"]
    tools_str = conversation["tools"]

    # ===== system prompt =====
    system_prompt = f"""<|im_start|>system
{system_value}

# Tools

You may call one or more functions to assist with the user query.

You are provided with function signatures within <tools></tools> XML tags:
<tools>
{tools_str}
</tools>

For each function call, return a json object with function name and arguments within <tool_call></tool_call> XML tags:
<tool_call>
{{"name": <function-name>, "arguments": <args-json-object>}}
</tool_call>
<|im_end|>
"""

    dialog = system_prompt

    # ===== 拼接所有角色的内容 =====
    for turn in conversation["conversations"]:
        role = turn["from"]
        value = turn["value"]

        if role == "human":
            dialog += f"<|im_start|>user\n{value}<|im_end|>\n"

        elif role == "function_call":
            content = turn.get("content", "")
            segment = f"<|im_start|>assistant\n"
            if content:
                segment += f"{content}\n"
            segment += f"<tool_call>\n{value}\n</tool_call><|im_end|>\n"
            dialog += segment

        elif role == "observation":
            dialog += f"<|im_start|>user\n<tool_response>\n{value}\n</tool_response><|im_end|>\n"

        elif role == "assistant" or role == "gpt":
            dialog += f"<|im_start|>assistant\n{value}<|im_end|>\n"

        else:
            raise ValueError(f"Unknown role: {role}")

    # 模型继续生成 assistant
    dialog += "<|im_start|>assistant\n"

    # ===== 编码 =====
    enc = tokenizer(
        [dialog] * num,
        padding="max_length",
        truncation=True,
        max_length=max_length,
        return_tensors="pt",
        add_special_tokens=False
    )

    return enc


from pydantic import BaseModel, Field
from typing import List, Literal, Any, Optional
import json
import copy


# 单条消息结构
class Message(BaseModel):
    from_: Literal["human", "gpt", "observation"] = Field(alias="from")
    value: str
    content: Optional[Any] = None


# 单个对话结构（对应原 export 的字典）
class ConversationItem(BaseModel):
    system_prompt: str = ""
    tools: str = ""
    conversations: List[Message] = Field(default_factory=list)

    def clone(self):
        return copy.deepcopy(self)

    def add(self, role: Literal["human", "gpt", "observation"], value: Any, content: Any = None):
        if role == "observation":
            msg = Message(from_="observation", value=json.dumps(value, ensure_ascii=False), content=content)
        else:
            msg = Message(from_=role, value=value, content=content)
        self.conversations.append(msg)

    def export(self) -> dict:
        return self.model_dump(by_alias=True)


# ✅ 批量维护多个 conversation 的结构
class ConversationList(BaseModel):
    items: List[ConversationItem] = Field(default_factory=list)

    def add_conversation(self, conversation: ConversationItem):
        self.items.append(conversation)

    def export_all(self) -> List[dict]:
        return [conv.export() for conv in self.items]
# 创建单个对话
conv1 = ConversationItem(system_prompt="助手A", tools="[]")
conv1.add("human", "你好")
conv1.add("gpt", "你好！")

conv2 = ConversationItem(system_prompt="助手B", tools="[search]")
conv2.add("human", "帮我查天气")
conv2.add("observation", {"action": "search", "query": "天气"})

# 创建对话集合
conv_list = ConversationList()
conv_list.add_conversation(conv1)
conv_list.add_conversation(conv2)

print(conv_list.export_all())
