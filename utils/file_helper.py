import os
from typing import List, Union
from transformers import AutoTokenizer


class MarkdownTokenizerTool:
    """
    Markdown 文件处理与 Tokenizer 计算工具
    """

    def __init__(self, model_name_or_path: str):
<<<<<<< HEAD
        if not os.path.exists(model_name_or_path):
            raise FileNotFoundError(f"Tokenizer path not found: {model_name_or_path}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

    # ===========================================================
    # 🔹 读取与清理
    # ===========================================================
    @staticmethod
    def read_md_remove_empty_lines(file_path: str) -> List[str]:
        """读取 Markdown 文件并去除空行"""
=======
        """
        初始化 tokenizer
        :param model_name_or_path: 模型名称或本地 tokenizer 路径
        """
        if not os.path.exists(model_name_or_path):
            raise FileNotFoundError(f"Tokenizer path not found: {model_name_or_path}")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)

    @staticmethod
    def read_md_remove_empty_lines(file_path: str) -> List[str]:
        """
        读取 Markdown 文件并去除空行。
        :param file_path: Markdown 文件路径
        :return: 去除空行后的行列表
        """
>>>>>>> b6517ef668d9a64ccbb8ca43ac3797774a835347
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Markdown file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        cleaned_lines = [line.rstrip() for line in lines if line.strip()]
        return cleaned_lines

<<<<<<< HEAD
    def save_cleaned_md(self, file_path: str, output_path: str = None) -> str:
        """
        去除空行并保存为新 Markdown 文件。
        调用 read_md_remove_empty_lines() 进行清理。
        """
        # ✅ 正确调用清理函数
        cleaned_lines = self.read_md_remove_empty_lines(file_path)

        # 拼接文本，确保每行后有换行符
        cleaned_text = "\n".join(cleaned_lines) + "\n"

        # 自动生成输出文件名
        if output_path is None:
            base, ext = os.path.splitext(file_path)
            output_path = base + "_cleaned" + ext

        # 写入文件
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_text)

        print(f"✅ 已保存去空行后的 Markdown：{output_path}")
        print(f"📄 共 {len(cleaned_lines)} 行（已去除空行）")
        return output_path

    # ===========================================================
    # 🔹 Tokenizer 相关
    # ===========================================================
    def count_tokens(self, text: Union[str, List[str]]) -> int:
        """计算文本的 token 数"""
        if isinstance(text, list):
            text = "\n".join(text)
=======
    def count_tokens(self, text: Union[str, List[str]]) -> int:
        """
        计算文本或多行文本的 token 数量
        :param text: 文本字符串或字符串列表
        :return: token 数
        """
        if isinstance(text, list):
            text = "\n".join(text)

>>>>>>> b6517ef668d9a64ccbb8ca43ac3797774a835347
        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        return len(tokens)

    def encode_text(self, text: str):
<<<<<<< HEAD
        return self.tokenizer([text], return_tensors="pt")

    # ===========================================================
    # 🔹 分块逻辑（支持多块输出）
    # ===========================================================
    def chunk_until_token_limit(self, file_path: str, max_tokens: int = 2000) -> List[str]:
        """
        按行顺序拼接 Markdown 文本，直到 token 超出上限为止。
        超出时自动开始新块。若单行超过 max_tokens，直接报错。
        """
        # ✅ 调用去空行后的读取函数
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


if __name__ == "__main__":
    md_path = r"D:\PycharmProjects\robot\raw_data\联络中心办事指南及常见问题百问百答.md"
    model_path = r"./tokenizer"

    tool = MarkdownTokenizerTool(model_path)

    # 1️⃣ 去空行并保存
    cleaned_path = tool.save_cleaned_md(md_path)

    # 2️⃣ 分块
    chunks = tool.chunk_until_token_limit(cleaned_path, max_tokens=2048)

=======
        """
        返回 tokenizer 的编码结果（如 token ids）
        """
        return self.tokenizer([text], return_tensors="pt")

    def process_md_file(self, file_path: str, show_preview: bool = False) -> int:
        """
        综合执行：读取 Markdown → 去空行 → 计算 token 数
        :param file_path: Markdown 文件路径
        :param show_preview: 是否打印部分内容预览
        :return: token 数
        """
        lines = self.read_md_remove_empty_lines(file_path)
        if show_preview:
            print("\n".join(lines[:10]))
            print("...")

        token_count = self.count_tokens(lines)
        print(f"📘 文件: {file_path}")
        print(f"🔢 Token 总数: {token_count}")
        return token_count


if __name__ == "__main__":
    md_path = r"D:\PycharmProjects\robot\raw_data\富家汇常见问题.md"
    model_path = r"./tokenizer"

    tool = MarkdownTokenizerTool(model_path)
    tool.process_md_file(md_path, show_preview=True)
>>>>>>> b6517ef668d9a64ccbb8ca43ac3797774a835347
