import json
import re


def extract_single_json(text: str):
    """
    从字符串中提取第一个合法 JSON 对象（容错版）
    - 自动匹配最外层完整大括号
    - 支持跨行、多层嵌套
    - 自动修复 null、true、false 的大小写问题
    """
    # 匹配最外层完整 {}，通过栈来解析而不是正则贪婪匹配
    start = text.find("{")
    if start == -1:
        raise ValueError("未找到 '{' 起始符号。")

    stack = []
    for i, ch in enumerate(text[start:], start=start):
        if ch == "{":
            stack.append(i)
        elif ch == "}":
            stack.pop()
            if not stack:  # 栈清空，表示找到完整 JSON
                json_str = text[start:i + 1]
                break
    else:
        raise ValueError("未找到匹配的 '}' 结束符号。")

    # 预处理：修复常见非 JSON 合法问题
    json_str = json_str.strip()
    json_str = re.sub(r"(\s)null(\s|[,}\]])", r"\1null\2", json_str)   # null
    json_str = re.sub(r"(\s)True(\s|[,}\]])", r"\1true\2", json_str)   # True
    json_str = re.sub(r"(\s)False(\s|[,}\]])", r"\1false\2", json_str) # False

    # 尝试解析
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        # 打印调试信息
        snippet = json_str[max(0, e.pos-40): e.pos+40]
        raise ValueError(f"解析 JSON 失败: {e}\n错误位置附近内容:\n{snippet}")


if __name__=="__main__":
    text ='''{"detected_toc": {"raw_text": null}, "new_structure": {"2.11.2 和公司合作的金融用户的合同如何查看？": {"children": null}, "2.11.3 工商业项目合作有哪些？": {"children": null}, "2.11.4 工商业半经销什么意思？": {"children": null}, "2.12 非全款电站对外合作关系答复": {"children": {"2.12.1 用户来电询问：签约的****公司是不是你们的公司和你们是什么关系？ （非全款）": {"children": null}}}, "三、 商务流程指导": {"children": {"3.1 渠道伙伴加盟的相关资料收集和条件": {"children": {"3.1.1收集客户信息": {"children": null}, "3.1.2 对接人：参考户用/工商业对接表格派单给对应的业务经理": {"children": null}, "3.1.3 户用加盟条件：": {"children": null}, "3.1.4 工商业加盟条件：": {"children": null}}}, "3.2 用户想订购安装电站的处理流程": {"children": {"3.2.1收集客户信息": {"children": null}, "3.2.2 对接人：参考户用/工商业对接表格派单给对应的业务经理": {"children": null}, "3.2.3条件和注意事项：": {"children": null}}}}}}'''
    print(extract_single_json(text))