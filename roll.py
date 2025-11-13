import torch
import json
import re

from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained('Qwen/Qwen2.5-0.5B-Instruct', padding_side="left",)
model = AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-0.5B-Instruct')

def process_function(conversation, tokenizer,num=2, max_length=2048):
    system_value = conversation["system_prompt"]
    tools_str = conversation["tools"]  # 保留转义
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
    # === 拼接对话内容 ===
    dialog = system_prompt
    spans = []
    for i, turn in enumerate(conversation["conversations"]):
        role = turn["from"]
        value = turn["value"]
        if role == "human":
            segment = f"<|im_start|>user\n{value}<|im_end|>\n"
        elif role == "function_call":
            content = turn.get("content", "")
            segment = f"<|im_start|>assistant"
            if content:
                segment += f"\n{content}"
            segment += f"\n<tool_call>\n{value}\n</tool_call><|im_end|>\n"
        elif role == "observation":
            segment = f"<|im_start|>user\n<tool_response>\n{value}\n</tool_response><|im_end|>\n"
        elif role == "gpt":
            segment = f"<|im_start|>assistant\n{value}<|im_end|>\n"
        else:
            raise ValueError(f"Unknown role: {role}")
        dialog += segment
    dialog+=f"<|im_start|>assistant\n"
    # === 编码并生成 input_ids 和 label_ids ===
    enc = tokenizer([dialog]*num, add_special_tokens=False, max_length=max_length,truncation=True,padding='max_length',return_tensors='pt')
    # enc = tokenizer(dialog, return_offsets_mapping=True, add_special_tokens=False, max_length=max_length,truncation=True)
    return enc

class BatchRolloutEngine:
    def __init__(self, model, tokenizer, process_function):
        """
        model: HF causal LM
        tokenizer: HF tokenizer
        process_function: 你给的函数，用于将 conversation dict 转成训练样本
        """
        self.model = model
        self.tokenizer = tokenizer
        self.process_function = process_function

    # ===========================
    # 工具函数：提取 <tool_call> 结构
    # ===========================
    def extract_tool_call(self, text: str):
        pattern = r"<tool_call>\s*(.*?)\s*</tool_call>"
        m = re.search(pattern, text, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(1))
        except Exception:
            return None

    # ===========================
    # 工具函数：执行模拟工具
    # ===========================
    def simulate_tool(self, call_dict):
        return {"tool_executed": call_dict["name"], "args": call_dict["arguments"]}

    # ===========================
    # Step 1: 生成 batch 初始回答
    # ===========================
    def generate_initial_batch(self, conversation, num_samples, max_new_tokens):
        model_inputs = self.process_function(conversation, self.tokenizer)
        with torch.no_grad():
            prompt_response_ids = self.model.generate(**model_inputs,
                                                      max_new_tokens=max_new_tokens,
                                                      temperature=0.9,
                                                      top_p=1,
                                                      top_k=50)
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, prompt_response_ids)
        ]

        response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

        return response

    # ===========================
    # Step 2: 构建 num_samples 条初始轨迹
    # ===========================
    def build_initial_trajectories(self, system_prompt, tools_str, user_input, answers):
        trajectories = []
        for ans in answers:
            trajectories.append({
                "system_prompt": system_prompt,
                "tools": tools_str,
                "conversations": [
                    {"from": "human", "value": user_input},
                    {"from": "gpt", "value": ans}
                ]
            })
        return trajectories

    # ===========================
    # Step 3: 对多个轨迹进行下一步 rollout（Batch）
    # ===========================
    def rollout_next_step_batch(self, trajectories, max_new_tokens):

        batch_input_ids = []
        batch_attention_mask = []

        # 1) 将所有轨迹 encode 并收集
        for conv in trajectories:
            proc = self.process_function(conv, self.tokenizer)
            batch_input_ids.append(proc["input_ids"])
            batch_attention_mask.append(proc["attention_mask"])

        # 2) 对 batch pad
        max_len = max(len(x) for x in batch_input_ids)
        padded_ids, padded_masks = [], []

        for ids, mask in zip(batch_input_ids, batch_attention_mask):
            pad_len = max_len - len(ids)
            padded_ids.append(ids + [self.tokenizer.pad_token_id] * pad_len)
            padded_masks.append(mask + [0] * pad_len)

        input_ids = torch.tensor(padded_ids).to(self.model.device)
        attention_mask = torch.tensor(padded_masks).to(self.model.device)

        # 3) 批量生成
        outputs = self.model.generate(
            input_ids=input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.9,
            top_p=0.9,
        )

        # 4) 抽取新增内容
        new_texts = []
        for i in range(len(trajectories)):
            orig_len = len(batch_input_ids[i])
            new_text = self.tokenizer.decode(outputs[i][orig_len:], skip_special_tokens=False)
            new_texts.append(new_text)

        return new_texts

    # ===========================
    # Step 4: 把新的 assistant 输出追加到轨迹
    # ===========================
    def append_to_trajectories(self, trajectories, new_texts):

        for conv, txt in zip(trajectories, new_texts):

            # 检查是否为 tool_call
            call = self.extract_tool_call(txt)
            if call is not None:
                conv["conversations"].append({
                    "from": "function_call",
                    "content": txt,
                    "value": json.dumps(call, ensure_ascii=False)
                })

                # 生成 observation
                tool_result = self.simulate_tool(call)
                conv["conversations"].append({
                    "from": "observation",
                    "value": json.dumps(tool_result, ensure_ascii=False)
                })
            else:
                conv["conversations"].append({
                    "from": "gpt",
                    "value": txt
                })

    # ===========================
    # 顶层 API：一次 rollout 生成多条完整轨迹
    # ===========================
    def rollout(
        self,
        system_prompt,
        tools_str,
        user_input,
        num_samples=4,
        rollout_steps=3,
        max_new_tokens=80
    ):
        """
        1. 用户输入 → 并行生成 num_samples 个初始回答
        2. 每个回答独立变成一条 trajectory
        3. 对所有 trajectory 并行 rollout N 步
        4. 返回 num_samples 条 trajectory
        """

        # Step 1: 初始对话
        init_conv = {
            "system_prompt": system_prompt,
            "tools": tools_str,
            "conversations": [
                {"from": "human", "value": user_input}
            ]
        }

        # Step 2: 多回答采样
        answers = self.generate_initial_batch(
            conversation=init_conv,
            num_samples=num_samples,
            max_new_tokens=max_new_tokens
        )

        # Step 3: 构建多条轨迹
        trajectories = self.build_initial_trajectories(
            system_prompt, tools_str, user_input, answers
        )

        # Step 4: rollout 后续 steps
        for _ in range(rollout_steps):
            new_texts = self.rollout_next_step_batch(trajectories, max_new_tokens)
            self.append_to_trajectories(trajectories, new_texts)

        return trajectories
engine = BatchRolloutEngine(model, tokenizer, process_function)

trajectories = engine.rollout(
    system_prompt="",
    tools_str='''{
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of a location, the user should supply a location first.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    }''',
    user_input="查询北京的天气",
    num_samples=4,       # 生成4条轨迹
    rollout_steps=3,     # 每条轨迹继续滚动3步
    max_new_tokens=128
)
