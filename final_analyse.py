import os
import json
from openai import OpenAI
from utils.file_helper import MarkdownTokenizerTool
from utils.extract_json import extract_single_json

# ===========================
# 🔹 初始化 DeepSeek 客户端
# ===========================
client = OpenAI(
    api_key="sk-dcb3caa7963645669e3205cae1f39464",
    base_url="https://api.deepseek.com"
)


# =======================================================
# 🧠 1️⃣ 抽取函数：从 Markdown 块中提取层级结构
# =======================================================
def analyze_md_tree_with_deepseek(previous_structure, md_text):
    """调用 DeepSeek 模型抽取当前块的结构"""

    prompt = f'''🤖 Role  
你是一名 **Markdown 文档结构增量分析助手**，负责根据输入文本自动更新文档的结构信息。  
文档结构由两个部分组成：  
1. `目录结构（toc）`：保留原文的目录文本；  
2. `标题层级结构（outline）`：由 Markdown 标题（#、##、### …）组成的层级树。  

---

# 💬 任务目标
根据输入：
- `previous_structure`：上一次处理后的结构（包含 toc 与 outline）；  
- `current_chunk`：当前新增的 Markdown 文本；  

分析当前块中的变化，并在不丢失旧数据的前提下：
- **增量更新**目录内容（若检测到目录章节）；  
- **增量更新**标题层级结构；  
- 保持层级连续、无重复。

---

# ⚙️ 规则

## 1️⃣ 目录检测（TOC 更新）
- 若检测到“目录”、“Contents”、“Table of Contents”等关键词：  
  - 提取该部分完整原文作为新的目录内容；  
  - 若之前已有目录，则进行**合并或更新**（保留全部独立目录文本）；  
  - 目录不参与标题层级结构分析。

## 2️⃣ 标题层级更新（Outline 更新）
- 识别 Markdown 标题（# 至 ######）；  
- 仅新增 `current_chunk` 中的新标题；  
- 若标题延续上层结构（例如上一部分以 “2.3” 结束，本段从 “2.3.1” 开始），  
  自动挂载到正确的父级下；  
- 按文本出现顺序构建，不重排、不丢失。

## 3️⃣ 输出要求
- 输出 **完整的更新后结构**，包含两部分：  
  1. `检测到的目录`（若有则保留原文；可包含多段目录）；  
  2. `合并后的标题层级结构`。  
- 使用 Markdown 层级格式表示结构：
  ```markdown
  # 一级标题
    - 二级标题
      - 三级标题
  ```
- 不输出 JSON、不解释、不添加说明。

---

# 📥 输入格式
```
=== previous_structure ===
{previous_structure if previous_structure else "无"}

=== current_chunk ===
{md_text}
```

---

# 📤 输出格式
```
检测到的目录：
（若存在目录则保留原文）

# 一级标题
  - 二级标题
    - 三级标题
```

'''

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    try:

        return content
    except Exception:
        print("⚠️ 模型输出非纯JSON，请手动检查：\n", content)
        return None

if __name__ == "__main__":
    model_path = r"D:\PycharmProjects\robot\utils\tokenizer"
    cleaned_path = r"D:\PycharmProjects\robot\raw_data\联络中心办事指南及常见问题百问百答_cleaned.md"

    tool = MarkdownTokenizerTool(model_path)
    chunks = tool.chunk_until_token_limit(cleaned_path, max_tokens=2048)
    previous_structure = None  # 初始为空

    for idx, chunk in enumerate(chunks, 1):
        print(f"\n=== 🧩 正在分析第 {idx}/{len(chunks)} 块 ===")
        result = analyze_md_tree_with_deepseek(previous_structure, chunk)


        # Step 2️⃣: 如果不是第一块，用大模型智能合并

        previous_structure = result

        # Step 3️⃣: 保存中间结果
        with open(f"merged_progress_{idx}.md", "a", encoding="utf-8") as f:
            f.write(previous_structure + "\n")
        # with open(f"merged_progress_{idx}.json", "w", encoding="utf-8") as f:
        #     json.dump(previous_structure, f, ensure_ascii=False, indent=2)

        print(f"✅ 第 {idx} 块处理完成，结构已更新。")

