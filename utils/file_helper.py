import os
from typing import List, Union
from transformers import AutoTokenizer


class MarkdownTokenizerTool:
    """
    Markdown 文件处理与 Tokenizer 计算工具
    """

    def __init__(self, model_name_or_path: str):
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
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Markdown file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        cleaned_lines = [line.rstrip() for line in lines if line.strip()]
        return cleaned_lines

    def count_tokens(self, text: Union[str, List[str]]) -> int:
        """
        计算文本或多行文本的 token 数量
        :param text: 文本字符串或字符串列表
        :return: token 数
        """
        if isinstance(text, list):
            text = "\n".join(text)

        tokens = self.tokenizer.encode(text, add_special_tokens=False)
        return len(tokens)

    def encode_text(self, text: str):
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
