# <<<<<<< HEAD
# # from markdown_it.rules_block import heading
# # from openai import OpenAI
# # import json
# # from utils.file_helper import MarkdownTokenizerTool
# # # 如果你是自建 deepseek 服务 / 本地 vLLM / DashScope 接口，请改成对应 base_url
# # client = OpenAI(
# #     api_key="sk-dcb3caa7963645669e3205cae1f39464",
# #     base_url="https://api.deepseek.com"
# # )
# #
# #
# # previous_structure=None
# # # ========== 2. Markdown 数据 ==========
# # md_text = ''''''
# #
# # # ========== 3. Prompt 构造 ==========
# # # ✅ 使用 f-string 来插入 md_text
# # prompt = f"""
# # 你是一名 Markdown 文档结构分析助手。
# #
# # 【任务目标】
# # 我会分段提供 Markdown 文本（current_chunk），请你从本段中**抽取新的标题层级结构**，并构建目录树。
# # 你需要结合上一段的结构（previous_structure）来保持层级连续性，但不能重复前一段已抽取的内容。
# #
# # 【抽取规则】
# # 1. 只处理当前段（current_chunk）中的新内容，不要重复 previous_structure 中已有的标题。
# # 2. 如果发现标题层级延续自上一段（例如上一段以 "1.2" 结束，当前段从 "1.2.1" 开始），应正确嵌入对应的上层标题下。
# # 3. 如果文本中存在“目录”、“Contents”、“Table of Contents”等部分，请将该部分**单独保存**到 "detected_toc" 字段中，不参与结构树构建。
# # 4. 输出结果中必须包含两个部分：
# #    - "detected_toc"：保存原文中目录部分的原始文本；
# #    - "new_structure"：当前段新增的标题层级树（不包含重复内容）。
# # 5. 每个节点都必须包含 "children" 键，即使为空对象。
# # 6. 按标题在文中出现的顺序构建层级，不要重新排序。
# # 7. 输出必须为**严格 JSON 格式**，不要附带说明、注释或多余文本。
# #
# # 【输出格式】
# # {{
# #   "detected_toc": {{
# #     "raw_text": "目录原文文本（若无则为 null）"
# #   }},
# #   "new_structure": {{
# #     "标题1": {{
# #       "children": {{
# #         "子标题1": {{"children": {{}}}},
# #         "子标题2": {{"children": {{}}}}
# #       }}
# #     }}
# #   }}
# # }}
# #
# # 【输入数据】
# # === 上一段已抽取的层级结构 ===
# # {previous_structure}
# #
# # === 当前段 Markdown 文本 ===
# # {md_text}
# #
# # 【输出要求】
# # - 只输出合法 JSON。
# # - 不要添加任何解释或额外文字。
# # - JSON 必须可以直接解析。
# # """
# #
# #
# #
# #
# # # ========== 4. 调用 DeepSeek 模型 ==========
# # def analyze_md_tree_with_deepseek(prompt: str):
# #     response = client.chat.completions.create(
# #         model="deepseek-chat",  # 或 deepseek-coder / DeepSeek-R1-Distill-Llama-70B
# #         messages=[{"role": "user", "content": prompt}],
# #         temperature=0
# #     )
# #
# #     content = response.choices[0].message.content.strip()
# #     try:
# #         tree = json.loads(content)
# #         return tree
# #     except Exception:
# #         print("⚠️ 模型输出非纯JSON，请手动查看：\n", content)
# #         return None
# #
# #
# # # ========== 5. 执行并打印结果 ==========
# # if __name__ == "__main__":
# #     model_path = r"D:\PycharmProjects\robot\utils\tokenizer"
# #
# #     tool = MarkdownTokenizerTool(model_path)
# #     cleaned_path = r'D:\PycharmProjects\robot\raw_data\联络中心办事指南及常见问题百问百答_cleaned.md'
# #     chunks = tool.chunk_until_token_limit(cleaned_path, max_tokens=2048)
# #
# #
# #     result = analyze_md_tree_with_deepseek(prompt)
# #     if result:
# #         print(json.dumps(result, ensure_ascii=False, indent=2))
# import os
# import json
# from copy import deepcopy
# from openai import OpenAI
# from utils.file_helper import MarkdownTokenizerTool
#
#
# # ========== DeepSeek 客户端 ==========
# =======
# from markdown_it.rules_block import heading
# from openai import OpenAI
# import json
#
# # 如果你是自建 deepseek 服务 / 本地 vLLM / DashScope 接口，请改成对应 base_url
# >>>>>>> b6517ef668d9a64ccbb8ca43ac3797774a835347
# client = OpenAI(
#     api_key="sk-dcb3caa7963645669e3205cae1f39464",
#     base_url="https://api.deepseek.com"
# )
# <<<<<<< HEAD
#
#
# # =======================================================
# # 🧩 结构合并工具
# # =======================================================
#
#
#
#
#
#
# # =======================================================
# # 🧠 模型调用函数
# # =======================================================
# def analyze_md_tree_with_deepseek(previous_structure, md_text):
#     """调用 DeepSeek 分析当前块"""
#     prompt = f"""你是一名 Markdown 文档结构分析助手。
#
# 【任务目标】
# 我会分段提供 Markdown 文本（current_chunk），请你从本段中**抽取新的标题层级结构**，并构建目录树。
# 你需要结合上一段的结构（previous_structure）来保持层级连续性，但不能重复前一段已抽取的内容。
#
# 【抽取规则】
# 1. 只处理当前段（current_chunk）中的新内容，不要重复 previous_structure 中已有的标题。
# 2. 如果发现标题层级延续自上一段（例如上一段以 "1.2" 结束，当前段从 "1.2.1" 开始），应正确嵌入对应的上层标题下。
# 3. 如果文本中存在“目录”、“Contents”、“Table of Contents”等部分，请将该部分**单独保存**到 "detected_toc" 字段中，不参与结构树构建。
# 4. 输出结果中必须包含两个部分：
#    - "detected_toc"：保存原文中目录部分的原始文本；
#    - "new_structure"：当前段新增的标题层级树（不包含重复内容）。
# 5. 每个节点都必须包含 "children" 键，即使为空对象。
# 6. 按标题在文中出现的顺序构建层级，不要重新排序。
# 7. 输出必须为**严格 JSON 格式**，不要附带说明、注释或多余文本。
#
# 【输出格式】
# {{
#   "detected_toc": {{
#     "raw_text": "目录原文文本（若无则为 null）"
#   }},
#   "new_structure": {{
#     "标题1": {{
#       "children": {{
#         "子标题1": {{"children": {{}}}},
#         "子标题2": {{"children": {{}}}}
# =======
# # ========== 2. Markdown 数据 ==========
# md_text = """L1 | 1.1 渠道招募合伙人信息反馈 | [0, 19)
# L1 | 1.1.1 富家汇的信息推广和适用业务范围是什么？ | [19, 87)
# L1 | A、登录方式： | [87, 204)
# L1 | B、合伙人绑定渠道伙伴的三种方式 | [204, 385)
# L1 | C、注意事项： | [385, 854)
# L1 | 1.2 合伙人注册注意事项 | [854, 871)
# L1 | 1.2.1 合伙人要求是什么？ | [871, 970)
# L1 | 1.2.2 合伙人注册步骤 | [970, 1124)
# L1 | 1.2.3 合伙人完成签约的具体标准 | [1124, 1311)
# L1 | 1.3 渠道伙伴相关问题 | [1311, 1327)
# L1 | 1.3.1 渠道伙伴如何注册为富家汇合伙人 | [1327, 1482)
# L1 | 1.3.2 系统提示子账户不能注册直营合伙人 | [1482, 1536)
# L1 | 1.3.3 渠道伙伴有录单及交付需求 | [1536, 1781)
# L1 | 1.4 线索录入 | [1781, 1793)
# L1 | 1.4.1 合伙人线索录入的条件 | [1793, 1824)
# L1 | 1.4.2 接单区域范围和线索的现勘范围不一致，是否可以做线索录入 | [1824, 1909)
# L1 | 1.5 结算相关问题 | [1909, 1923)
# L1 | 1.5.1 灵活用工和对公付款的区别 | [1923, 2045)
# L1 | 1.5.2 业务费用及税点 | [2045, 2208)
# L1 | 1.5.3 信息不一致，可以结算吗 | [2208, 2267)
# L1 | 1.5.4 费用结算以哪个时间点为准享受政策 | [2267, 2342)
# L1 | 1.5.5 其他费用明细及税点 | [2342, 2383)
# """
#
# # ========== 3. Prompt 构造 ==========
# # ✅ 使用 f-string 来插入 md_text
# prompt = f"""
# 你是一名 Markdown 文档结构分析助手。
#
# 以下是一份标题列表，每一行包含编号、标题、以及在原文中的位置区间。
#
# 请根据这些标题的编号和逻辑顺序，生成一个嵌套的 JSON 结构，表示它们的层级关系。
#
# 输出要求：
# - 以纯 JSON 格式输出；
# - 每个节点的键为“编号 + 空格 + 标题”；
# - 每个节点的值为一个对象，只包含一个键 "children"；
# - "children" 的值是同样结构的子节点对象；
# - 无子节点时，"children" 为空对象；
# - 不输出任何说明或解释。
#
# 示例输出：
# {{
#   "1.1 渠道招募合伙人信息反馈": {{
#     "children": {{
#       "1.1.1 富家汇的信息推广和适用业务范围是什么？": {{
#         "children": {{
#           "A、登录方式：": {{"children": {{}}}},
#           "B、合伙人绑定渠道伙伴的三种方式": {{"children": {{}}}},
#           "C、注意事项：": {{"children": {{}}}}
#         }}
# >>>>>>> b6517ef668d9a64ccbb8ca43ac3797774a835347
#       }}
#     }}
#   }}
# }}
#
# <<<<<<< HEAD
# 【输入数据】
# === 上一段已抽取的层级结构 ===
# {json.dumps(previous_structure, ensure_ascii=False) if previous_structure else "null"}
#
# === 当前段 Markdown 文本 ===
# {md_text}
#
# 【输出要求】
# - 只输出合法 JSON。
# - 不要添加任何解释或额外文字。
# - JSON 必须可以直接解析。
# """
#
#     response = client.chat.completions.create(
#         model="deepseek-chat",
# =======
# 下面是输入数据：
# {md_text}
# """
#
# # ========== 4. 调用 DeepSeek 模型 ==========
# def analyze_md_tree_with_deepseek(prompt: str):
#     response = client.chat.completions.create(
#         model="deepseek-chat",  # 或 deepseek-coder / DeepSeek-R1-Distill-Llama-70B
# >>>>>>> b6517ef668d9a64ccbb8ca43ac3797774a835347
#         messages=[{"role": "user", "content": prompt}],
#         temperature=0
#     )
#
#     content = response.choices[0].message.content.strip()
#     try:
#         tree = json.loads(content)
#         return tree
#     except Exception:
#         print("⚠️ 模型输出非纯JSON，请手动查看：\n", content)
#         return None
#
#
# <<<<<<< HEAD
# # =======================================================
# # 🚀 主流程：循环处理 + 实时合并
# # =======================================================
# if __name__ == "__main__":
#     model_path = r"D:\PycharmProjects\robot\utils\tokenizer"
#     cleaned_path = r"D:\PycharmProjects\robot\raw_data\联络中心办事指南及常见问题百问百答_cleaned.md"
#
#     tool = MarkdownTokenizerTool(model_path)
#     chunks = tool.chunk_until_token_limit(cleaned_path, max_tokens=2048)
#
#     merged_structure = None  # ✅ 从空开始
#
#     for idx, chunk in enumerate(chunks, 1):
#         print(f"\n=== 🧩 正在分析第 {idx}/{len(chunks)} 块 ===")
#
#         # 调用模型（传入当前合并结构作为 previous_structure）
#         result = analyze_md_tree_with_deepseek(merged_structure, chunk)
#         if not result:
#             print(f"⚠️ 第 {idx} 块模型输出异常，跳过。")
#             continue
#
#         # ✅ 合并本轮结构
#         if idx > 1:
#             merged_structure = merge_two_structures(merged_structure, result)
#         else:
#             merged_structure = result
#
#         # 保存中间结果（防止崩溃丢失）
#         with open("merged_progress.json", "w", encoding="utf-8") as f:
#             json.dump(merged_structure, f, ensure_ascii=False, indent=2)
#
#         print(f"✅ 已合并到第 {idx} 块，当前结构已更新。")
#
#     # 输出最终结果
#     with open("final_merged_markdown_structure.json", "w", encoding="utf-8") as f:
#         json.dump(merged_structure, f, ensure_ascii=False, indent=2)
#
#     print("\n🎉 全部完成，最终合并结构已保存到 final_merged_markdown_structure.json ✅")
# =======
# # ========== 5. 执行并打印结果 ==========
# if __name__ == "__main__":
#     result = analyze_md_tree_with_deepseek(prompt)
#     if result:
#         print(json.dumps(result, ensure_ascii=False, indent=2))
# >>>>>>> b6517ef668d9a64ccbb8ca43ac3797774a835347
