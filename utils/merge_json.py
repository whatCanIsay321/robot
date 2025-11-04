import json
from copy import deepcopy

def merge_children(base_children, new_children):
    """递归合并子层级"""
    for key, val in new_children.items():
        if key in base_children:
            # 已存在同名标题 → 合并其子层级
            merge_children(base_children[key]["children"], val.get("children", {}))
        else:
            # 新标题 → 直接添加
            base_children[key] = deepcopy(val)
    return base_children


def merge_markdown_structures(struct_list):
    """
    合并多个模型输出的 markdown 层级结构结果。
    参数:
        struct_list: 每个元素是模型的 JSON 输出（dict），形如：
        {
          "detected_toc": {"raw_text": "..."},
          "new_structure": {...}
        }
    返回:
        {
          "detected_toc": {"raw_text": "..."},
          "merged_structure": {...}
        }
    """
    merged = {
        "detected_toc": {"raw_text": None},
        "merged_structure": {}
    }

    for struct in struct_list:
        # 1️⃣ 合并 detected_toc
        toc_text = struct.get("detected_toc", {}).get("raw_text")
        if toc_text and not merged["detected_toc"]["raw_text"]:
            merged["detected_toc"]["raw_text"] = toc_text

        # 2️⃣ 合并结构
        new_structure = struct.get("new_structure", {})
        merged["merged_structure"] = merge_children(merged["merged_structure"], new_structure)

    return merged


# =====================
# ✅ 使用示例
# =====================
if __name__ == "__main__":
    # 模拟模型输出的三段结果
    chunk1 = {
        "detected_toc": {"raw_text": "# 目录\n- 1. 概述\n- 2. 使用说明"},
        "new_structure": {
            "1. 概述": {"children": {"1.1 背景介绍": {"children": {}}}}
        }
    }

    chunk2 = {
        "detected_toc": {"raw_text": None},
        "new_structure": {
            "1. 概述": {"children": {"1.2 系统结构": {"children": {}}}}
        }
    }

    chunk3 = {
        "detected_toc": {"raw_text": None},
        "new_structure": {
            "2. 使用说明": {
                "children": {
                    "2.1 登录": {"children": {}},
                    "2.2 注册": {"children": {}}
                }
            }
        }
    }

    merged = merge_markdown_structures([chunk1, chunk2, chunk3])

    print(json.dumps(merged, ensure_ascii=False, indent=2))
