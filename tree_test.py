#
# import json
# import re
# import requests
# from typing import List, Dict, Any
# from dataclasses import dataclass
# from abc import ABC, abstractmethod
#
#
# # ----------------------------
# # TreeNode 数据结构
# # ----------------------------
# @dataclass
# class TreeNode:
#     label: str
#     child: List['TreeNode'] = None
#
#     def __post_init__(self):
#         if self.child is None:
#             self.child = []
#
#     def to_dict(self) -> Dict[str, Any]:
#         result = {"label": self.label}
#         if self.child:
#             result["child"] = [child.to_dict() for child in self.child]
#         return result
#
#
# # ----------------------------
# # Markdown 文件处理器
# # ----------------------------
# class MarkdownProcessor:
#     """Markdown文件处理器"""
#
#     def read_markdown_file(self, file_path: str) -> str:
#         """读取Markdown文件内容"""
#         with open(file_path, 'r', encoding='utf-8') as f:
#             return f.read()
#
#     def extract_table_of_contents(self, content: str) -> List[Dict[str, Any]]:
#         """提取目录结构"""
#         toc = []
#         lines = content.split('\n')
#
#         for line in lines:
#             # 匹配标题行 (# ## ### 等)
#             match = re.match(r'^(#{1,6})\s+(.+)$', line.strip())
#             if match:
#                 level = len(match.group(1))
#                 title = match.group(2).strip()
#                 toc.append({
#                     'level': level,
#                     'title': title,
#                     'line': line
#                 })
#
#         return toc
#
#     def toc_to_markdown(self, toc: List[Dict[str, Any]], is_nested: bool = True) -> str:
#         """将目录结构转换为Markdown格式"""
#         if not toc:
#             return ""
#
#         result = []
#         for item in toc:
#             if is_nested:
#                 indent = "  " * (item['level'] - 1)
#                 result.append(f"{indent}- {item['title']}")
#             else:
#                 result.append(f"{'#' * item['level']} {item['title']}")
#
#         return '\n'.join(result)
#
#
# # ----------------------------
# # 抽象 LLM Client
# # ----------------------------
# class LLMClient(ABC):
#     """LLM客户端抽象基类"""
#
#     def __init__(self, config: Dict[str, Any]):
#         self.config = config
#         self.endpoint = config.get("endpoint")
#         self.api_key = config.get("apiKey")
#         self.model_name = config.get("modelName")
#         self.temperature = config.get("temperature", 0.7)
#         self.max_tokens = config.get("maxTokens", 2000)
#
#     @abstractmethod
#     def chat(self, messages: List[Dict]) -> Dict:
#         pass
#
#
# # ----------------------------
# # OpenAI 客户端实现
# # ----------------------------
# class OpenAIClient(LLMClient):
#     """OpenAI 客户端实现"""
#
#     def chat(self, messages: List[Dict]) -> Dict:
#         headers = {
#             "Authorization": f"Bearer {self.api_key}",
#             "Content-Type": "application/json",
#         }
#         data = {
#             "model": self.model_name,
#             "messages": messages,
#             "temperature": self.temperature,
#             "max_tokens": self.max_tokens,
#         }
#         response = requests.post(
#             f"{self.endpoint}/chat/completions", headers=headers, json=data
#         )
#         if response.status_code == 200:
#             result = response.json()
#             return {"answer": result["choices"][0]["message"]["content"]}
#         else:
#             raise Exception(f"OpenAI API 调用失败: {response.status_code}, {response.text}")
#
#
# # ----------------------------
# # 领域树生成器
# # ----------------------------
# class DomainTreeGenerator:
#     """领域树生成器"""
#
#     def __init__(self, llm_client: LLMClient, language: str = "zh"):
#         self.llm_client = llm_client
#         self.language = language
#
#     def get_label_prompt(self, text: str,
#                          global_prompt: str = "",
#                          domain_tree_prompt: str = "") -> str:
#         """生成领域分类提示词"""
#         if self.language == "zh":
#             return self._get_chinese_prompt(text, global_prompt, domain_tree_prompt)
#         else:
#             return self._get_english_prompt(text, global_prompt, domain_tree_prompt)
#
#     def _get_chinese_prompt(self, text: str,
#                             global_prompt: str = "",
#                             domain_tree_prompt: str = "") -> str:
#         """中文提示词模板"""
#         global_rule = f"- 在后续的任务中，你务必遵循这样的规则：{global_prompt}" if global_prompt else ""
#         domain_rule = f"- 在生成标签时，你务必遵循这样的规则：{domain_tree_prompt}" if domain_tree_prompt else ""
#
#         return f"""
# # Role: 领域分类专家 & 知识图谱专家
# - Description: 作为一名资深的领域分类专家和知识图谱专家，擅长从文本内容中提取核心主题，构建分类体系，并输出规定 JSON 格式的标签树。
# {global_rule}
#
# ## Skills:
# 1. 精通文本主题分析和关键词提取
# 2. 擅长构建分层知识体系
# 3. 熟练掌握领域分类方法论
# 4. 具备知识图谱构建能力
# 5. 精通JSON数据结构
#
# ## Goals:
# 1. 分析书籍目录内容
# 2. 识别核心主题和关键领域
# 3. 构建两级分类体系
# 4. 确保分类逻辑合理
# 5. 生成规范的JSON输出
#
# ## Workflow:
# 1. 仔细阅读完整的书籍目录内容
# 2. 提取关键主题和核心概念
# 3. 对主题进行分组和归类
# 4. 构建一级领域标签
# 5. 为适当的一级标签添加二级标签
# 6. 检查分类逻辑的合理性
# 7. 生成符合格式的JSON输出
#
# ## 需要分析的目录
# {text}
#
# ## 限制
# 1. 一级领域标签数量5-10个
# 2. 二级领域标签数量1-10个
# 3. 最多两层分类层级
# 4. 分类必须与原始目录内容相关
# 5. 输出必须符合指定 JSON 格式，不要输出 JSON 外其他任何不相关内容
# 6. 标签的名字最多不要超过 6 个字
# 7. 在每个标签前加入序号（序号不计入字数）
# {domain_rule}
#
# ## OutputFormat:
# ```json
# [
#   {{
#     "label": "1 一级领域标签",
#     "child": [
#       {{"label": "1.1 二级领域标签1"}},
#       {{"label": "1.2 二级领域标签2"}}
#     ]
#   }},
#   {{
#     "label": "2 一级领域标签(无子标签)"
#   }}
# ]
# ```"""
#
#     def _get_english_prompt(self, text: str,
#                             global_prompt: str = "",
#                             domain_tree_prompt: str = "") -> str:
#         return f"Catalog:\n{text}\nOutput JSON tree with labels."
#
#     def generate_domain_tree(self, toc_text: str,
#                              global_prompt: str = "",
#                              domain_tree_prompt: str = "") -> List[TreeNode]:
#         """生成领域树"""
#         prompt = self.get_label_prompt(toc_text, global_prompt, domain_tree_prompt)
#
#         response = self.llm_client.chat([{"role": "user", "content": prompt}])
#         raw_answer = response["answer"]
#
#         try:
#             json_match = re.search(r'```json\s*(.*?)\s*```', raw_answer, re.DOTALL)
#             if json_match:
#                 json_str = json_match.group(1)
#             else:
#                 json_str = raw_answer
#
#             tree_data = json.loads(json_str)
#             return self._parse_tree_data(tree_data)
#         except json.JSONDecodeError as e:
#             raise ValueError(f"Failed to parse LLM response as JSON: {e}")
#
#     def _parse_tree_data(self, data: List[Dict[str, Any]]) -> List[TreeNode]:
#         nodes = []
#         for item in data:
#             node = TreeNode(label=item['label'])
#             if 'child' in item and item['child']:
#                 node.child = self._parse_tree_data(item['child'])
#             nodes.append(node)
#         return nodes
#
#
# # ----------------------------
# # 领域树处理主类
# # ----------------------------
# class DomainTreeProcessor:
#     """领域树处理主类"""
#
#     def __init__(self, llm_client: LLMClient, language: str = "zh"):
#         self.markdown_processor = MarkdownProcessor()
#         self.tree_generator = DomainTreeGenerator(llm_client, language)
#
#     def process_markdown_to_domain_tree(self, file_path: str,
#                                         global_prompt: str = "",
#                                         domain_tree_prompt: str = "") -> List[TreeNode]:
#         """处理Markdown文件生成领域树"""
#         content = self.markdown_processor.read_markdown_file(file_path)
#         toc = self.markdown_processor.extract_table_of_contents(content)
#         toc_markdown = self.markdown_processor.toc_to_markdown(toc, is_nested=True)
#
#         domain_tree = self.tree_generator.generate_domain_tree(
#             toc_markdown, global_prompt, domain_tree_prompt
#         )
#
#         return domain_tree
#
#     def save_domain_tree(self, domain_tree: List[TreeNode], output_path: str):
#         tree_dict = [node.to_dict() for node in domain_tree]
#         with open(output_path, 'w', encoding='utf-8') as f:
#             json.dump(tree_dict, f, ensure_ascii=False, indent=2)
#
#
# # ----------------------------
# # 使用示例
# # ----------------------------
# if __name__ == "__main__":
#     config = {
#         "providerId": "deepseek",
#         "endpoint": "https://api.deepseek.com",
#         "apiKey": "sk-4d1e7b1474a14168be51ce21d6f1919f",
#         "modelName": "deepseek-chat",
#     }
#
#     llm_client = OpenAIClient(config)
#     processor = DomainTreeProcessor(llm_client, language="zh")
#
#     try:
#         domain_tree = processor.process_markdown_to_domain_tree(
#             r"D:\PycharmProjects\robot\raw_data\富家汇常见问题.md",
#             global_prompt="请确保分类准确",
#             # domain_tree_prompt="重点关注技术领域"
#         )
#
#         processor.save_domain_tree(domain_tree, "domain_tree.json")
#
#         print("领域树生成完成！")
#         for node in domain_tree:
#             print(f"- {node.label}")
#             for child in node.child:
#                 print(f"  - {child.label}")
#
#     except Exception as e:
#         print(f"处理失败: {e}")
import re
from typing import List, Dict


def extract_md_headings_with_range(file_path: str) -> List[Dict]:
    """
    提取 Markdown 文件中所有标题，并标注每个标题的字符起止区间。
    返回结构:
    [
        {
            "level": 1,
            "title": "渠道招募合伙人信息反馈",
            "line_no": 1,
            "start_index": 0,
            "end_index": 123
        },
        ...
    ]
    """
    pattern = re.compile(r'^(#{1,6})\s*(.+)$')
    headings = []

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
<<<<<<< HEAD
        cleaned_lines = [line.rstrip() for line in lines if line.strip()]
        lines = cleaned_lines
=======
>>>>>>> b6517ef668d9a64ccbb8ca43ac3797774a835347

    char_offset = 0
    for i, line in enumerate(lines):
        match = pattern.match(line.strip())
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            headings.append({
                "level": level,
                "title": title,
                "line_no": i + 1,
                "start_index": char_offset
            })
        char_offset += len(line)

    # 添加 end_index（下一个标题的 start_index 或全文末尾）
    with open(file_path, "r", encoding="utf-8") as f:
        full_text = f.read()
    file_length = len(full_text)

    for i, h in enumerate(headings):
        if i + 1 < len(headings):
            h["end_index"] = headings[i + 1]["start_index"]
        else:
            h["end_index"] = file_length

    return headings

if __name__ == "__main__":
<<<<<<< HEAD
    md_path = r"D:\PycharmProjects\robot\raw_data\联络中心办事指南及常见问题百问百答.md"
=======
    md_path = r"D:\PycharmProjects\robot\raw_data\富家汇常见问题.md"
>>>>>>> b6517ef668d9a64ccbb8ca43ac3797774a835347
    result = extract_md_headings_with_range(md_path)

    # 打印结果
    for h in result:
<<<<<<< HEAD
        # print(f"{h['title']}")
=======
>>>>>>> b6517ef668d9a64ccbb8ca43ac3797774a835347
        print(f"L{h['level']} | {h['title']} | [{h['start_index']}, {h['end_index']})")

    # 获取第一个标题下的全部原文内容
    with open(md_path, "r", encoding="utf-8") as f:
        text = f.read()

    first_section = text[result[0]["start_index"]:result[0]["end_index"]]
    print("\n=== 第一个标题下的完整内容 ===")
    print(first_section)

