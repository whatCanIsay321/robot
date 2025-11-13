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
