from markdown_it.rules_block import heading
from openai import OpenAI
import json

# 如果你是自建 deepseek 服务 / 本地 vLLM / DashScope 接口，请改成对应 base_url
client = OpenAI(
    api_key="sk-dcb3caa7963645669e3205cae1f39464",
    base_url="https://api.deepseek.com"
)
# ========== 2. Markdown 数据 ==========
md_text = """L1 | 1.1 渠道招募合伙人信息反馈 | [0, 19)
L1 | 1.1.1 富家汇的信息推广和适用业务范围是什么？ | [19, 87)
L1 | A、登录方式： | [87, 204)
L1 | B、合伙人绑定渠道伙伴的三种方式 | [204, 385)
L1 | C、注意事项： | [385, 854)
L1 | 1.2 合伙人注册注意事项 | [854, 871)
L1 | 1.2.1 合伙人要求是什么？ | [871, 970)
L1 | 1.2.2 合伙人注册步骤 | [970, 1124)
L1 | 1.2.3 合伙人完成签约的具体标准 | [1124, 1311)
L1 | 1.3 渠道伙伴相关问题 | [1311, 1327)
L1 | 1.3.1 渠道伙伴如何注册为富家汇合伙人 | [1327, 1482)
L1 | 1.3.2 系统提示子账户不能注册直营合伙人 | [1482, 1536)
L1 | 1.3.3 渠道伙伴有录单及交付需求 | [1536, 1781)
L1 | 1.4 线索录入 | [1781, 1793)
L1 | 1.4.1 合伙人线索录入的条件 | [1793, 1824)
L1 | 1.4.2 接单区域范围和线索的现勘范围不一致，是否可以做线索录入 | [1824, 1909)
L1 | 1.5 结算相关问题 | [1909, 1923)
L1 | 1.5.1 灵活用工和对公付款的区别 | [1923, 2045)
L1 | 1.5.2 业务费用及税点 | [2045, 2208)
L1 | 1.5.3 信息不一致，可以结算吗 | [2208, 2267)
L1 | 1.5.4 费用结算以哪个时间点为准享受政策 | [2267, 2342)
L1 | 1.5.5 其他费用明细及税点 | [2342, 2383)
"""

# ========== 3. Prompt 构造 ==========
# ✅ 使用 f-string 来插入 md_text
prompt = f"""
你是一名 Markdown 文档结构分析助手。

以下是一份标题列表，每一行包含编号、标题、以及在原文中的位置区间。

请根据这些标题的编号和逻辑顺序，生成一个嵌套的 JSON 结构，表示它们的层级关系。

输出要求：
- 以纯 JSON 格式输出；
- 每个节点的键为“编号 + 空格 + 标题”；
- 每个节点的值为一个对象，只包含一个键 "children"；
- "children" 的值是同样结构的子节点对象；
- 无子节点时，"children" 为空对象；
- 不输出任何说明或解释。

示例输出：
{{
  "1.1 渠道招募合伙人信息反馈": {{
    "children": {{
      "1.1.1 富家汇的信息推广和适用业务范围是什么？": {{
        "children": {{
          "A、登录方式：": {{"children": {{}}}},
          "B、合伙人绑定渠道伙伴的三种方式": {{"children": {{}}}},
          "C、注意事项：": {{"children": {{}}}}
        }}
      }}
    }}
  }}
}}

下面是输入数据：
{md_text}
"""

# ========== 4. 调用 DeepSeek 模型 ==========
def analyze_md_tree_with_deepseek(prompt: str):
    response = client.chat.completions.create(
        model="deepseek-chat",  # 或 deepseek-coder / DeepSeek-R1-Distill-Llama-70B
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    try:
        tree = json.loads(content)
        return tree
    except Exception:
        print("⚠️ 模型输出非纯JSON，请手动查看：\n", content)
        return None


# ========== 5. 执行并打印结果 ==========
if __name__ == "__main__":
    result = analyze_md_tree_with_deepseek(prompt)
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))