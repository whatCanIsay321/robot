import os
from typing import List, Union
from transformers import AutoTokenizer


class MarkdownTokenizerTool:
    """
    Markdown 文件处理与 Tokenizer 计算工具
    """

    # ===========================================================
    # 🔹 初始化
    # ===========================================================
    def __init__(self, model_name_or_path: str):
        """
        初始化 tokenizer
        :param model_name_or_path: 模型名称或本地 tokenizer 路径
        """
        if not os.path.exists(model_name_or_path):
            raise FileNotFoundError(f"Tokenizer path not found: {model_name_or_path}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

    # ===========================================================
    # 🔹 读取与清理
    # ===========================================================
    @staticmethod
    def read_md_remove_empty_lines(file_path: str) -> List[str]:
        """
        读取 Markdown 文件并去除空行。
        :param file_path: Markdown 文件路径
        :return: 去除空行后的行列表
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Markdown file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        cleaned_lines = [line.rstrip() for line in lines if line.strip()]
        return cleaned_lines

    def save_cleaned_md(self, file_path: str, output_path: str = None) -> str:
        """
        去除空行并保存为新 Markdown 文件。
        调用 read_md_remove_empty_lines() 进行清理。
        """
        cleaned_lines = self.read_md_remove_empty_lines(file_path)
        cleaned_text = "\n".join(cleaned_lines) + "\n"

        # 自动生成输出文件名
        if output_path is None:
            base, ext = os.path.splitext(file_path)
            output_path = base + "_cleaned" + ext

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"✅ 已保存去空行后的 Markdown：{output_path}")
        print(f"📄 共 {len(cleaned_lines)} 行（已去除空行）")
        return output_path

    # ===========================================================
    # 🔹 Tokenizer 相关
    # ===========================================================
    def count_tokens(self, text: Union[str, List[str]]) -> int:
        """
        计算文本的 token 数。
        :param text: 文本字符串或字符串列表
        :return: token 数量
        """
        if isinstance(text, list):
            text = "\n".join(text)
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        return len(tokens)

    def encode_text(self, text: str):
        """返回 tokenizer 的编码结果"""
        return self.tokenizer([text], return_tensors="pt")

    # ===========================================================
    # 🔹 分块逻辑（支持多块输出）
    # ===========================================================
    def chunk_until_token_limit(self, file_path: str, max_tokens: int = 2000) -> List[str]:
        """
        按行顺序拼接 Markdown 文本，直到 token 超出上限为止。
        超出时自动开始新块。若单行超过 max_tokens，直接报错。
        """
        lines = self.read_md_remove_empty_lines(file_path)

        chunks = []
        current_chunk = []
        current_tokens = 0

        for i, line in enumerate(lines, start=1):
            line_token_len = self.count_tokens(line)
            if line_token_len > max_tokens:
                raise ValueError(
                    f"❌ 第 {i} 行超出单块最大 token 限制！"
                    f" 当前行 {line_token_len} tokens > 限制 {max_tokens}。\n"
                    f"行内容预览：{line[:100]}..."
                )

            test_chunk = current_chunk + [line]
            token_len = self.count_tokens(test_chunk)

            if token_len > max_tokens:
                chunks.append("\n".join(current_chunk))
                print(f"📦 已保存第 {len(chunks)} 块，共 {current_tokens} tokens。")
                current_chunk = [line]
                current_tokens = line_token_len
            else:
                current_chunk.append(line)
                current_tokens = token_len

        if current_chunk:
            chunks.append("\n".join(current_chunk))
            print(f"📦 已保存第 {len(chunks)} 块，共 {current_tokens} tokens。")

        print(f"✅ 总共生成 {len(chunks)} 个块（每块 ≤ {max_tokens} tokens）")
        return chunks


# ===========================================================
# 🔹 运行示例
# ===========================================================
if __name__ == "__main__":
    # md_path = r"D:\PycharmProjects\robot\raw_data\联络中心办事指南及常见问题百问百答.md"
    # model_path = r"./tokenizer"
    #
    # tool = MarkdownTokenizerTool(model_path)
    #
    # # 1️⃣ 去空行并保存
    # cleaned_path = tool.save_cleaned_md(md_path)

    # 2️⃣ 分块
    # chunks = tool.chunk_until_token_limit(cleaned_path, max_tokens=2048)

    model_path = "./tokenizer"  # 你的 tokenizer 目录
    file_path = r"D:\PycharmProjects\robot\merged_progress_12.md"

    tool = MarkdownTokenizerTool(model_path)

    # 读取 Markdown 并去空行
    lines = tool.read_md_remove_empty_lines(file_path)

    # 计算 token 数
    token_count = tool.count_tokens(lines)

    print(f"🔢 文件共 {token_count} 个 tokens")