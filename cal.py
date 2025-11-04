from difflib import SequenceMatcher
from typing import List, Dict, Any, Tuple


def flatten_structure(structure: Dict[str, Any]) -> List[str]:
    """递归提取 new_structure 中所有标题"""
    titles = []
    for title, content in structure.items():
        titles.append(title)
        if "children" in content and content["children"]:
            titles.extend(flatten_structure(content["children"]))
    return titles


def find_best_line_span(input_str: str, lines: List[str]) -> Tuple[int, float, str]:
    """
    在 Markdown 行列表中查找与 input_str 最相似的行。
    返回 (行号, 相似度, 匹配行内容)
    """
    best_score, best_line_idx, best_line_text = 0.0, None, ""

    for i, line in enumerate(lines):
        score = SequenceMatcher(None, input_str.strip(), line.strip()).ratio()
        if score > best_score:
            best_score, best_line_idx, best_line_text = score, i, line

    return best_line_idx, best_score, best_line_text


def validate_extracted_structure_by_line(md_text: str, extracted_json: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    按行验证模型抽取的 Markdown 标题结构。
    从 Markdown 文本字符串中提取行，逐行匹配抽取标题。
    返回：每个标题的匹配行号、相似度、匹配行文本。
    """
    # 拆分 Markdown 字符串为行
    lines = [line.strip() for line in md_text.splitlines() if line.strip()]

    # 提取结构中的标题
    structure = extracted_json.get("new_structure", extracted_json)
    titles = flatten_structure(structure)

    results = []
    for title in titles:
        line_idx, score, matched_line = find_best_line_span(title, lines)
        results.append({
            "title": title,
            "found": score > 0.6,
            "match_score": round(score, 3),
            "line_number": line_idx + 1 if line_idx is not None else None,  # 1-based 行号
            "matched_line": matched_line
        })
    return results




if __name__ == "__main__":
    # ===== 示例 =====

    md_text = """# 目录
# 一、 产品类 .... 3
# 二、 业务模式和合作类型. 6
# 三、 商务流程指导.. .17
# 四、售后类.. 19
# 五、客服必备常见故障排查... .25
5.1 离线.. . 26
5.2 故障.. .. 26
5.3 低效能.. ...29
5.4 频繁故障. .29
5.5 屋顶漏雨. .30
5.6 房屋修缮. ..30
5.7 国网数据异常. ..31
5.8 舆情&客诉. ..... 31
5.9 故障提醒规则. ...33
六、疑难问题处理流程和对接话术.. . 35
6.1 疑难问题处理话术. . 35
6.2话务派单规则. .. 37
6.3售后系统操作指导. ..42
七、联络中心现场工作规范及业务流程指引. ...43
7.1 现场工作规范. ...43
7.2 话务坐席客服客服工作指引. .. 45
7.3微信群对接. ... 45
7.4工单审核和派单. ...46
# 联络中心办事指南及常见问题百问百答0
# 一、 产品类
# 1.1 组件类
# 1.1.1 组件板上为什么有色差？
答：您好，组件在生成过程中的生产工艺上会衍生出许多色系的电池片，属于行业内正常现象。天合光能内部标准把多种电池片划分为 4种色系，从而造成同类色系组件间存在轻微视觉差异；后续产品如有任何质量问题，天合光能将提供10年工艺质保以及 25（30）年线性功率质保。
# 1.1.2 组件板上有白色的斑点是什么情况？
答:您好，组件板上的白点是组件生产过程中印刷网版上自带的激光定位点，目前组件的每个大片电池片都有固定约 4个，不影响组件质量。
# 1.1.3 组件板的等级是怎么区分？
答：您好，您若是购买的是天合原装系统，您的产品配置的组件都是 Q1的一等品。
# 1.1.4 组件背光度怎么不一样？
答：您好，组件背面色差及漏光的组件不影响正常使用，DEC15MC20（II）组件享受天合 30年有限店里输出质保服务，请放心使用。
# 1.1.5 光伏组件要定期清洗吗？
答：您好，由于各地区天气情况及污染程度不同，对组件清洗周期暂不做统一规定。根据脏污程度，灰尘过指测试数据，清洗费，清洗后所提升的发电效率以及效益等测算确定清洗频率。
# 1.1.6 你们的产品配置，组件功率是多少的？
答：您好，我们是整套系统进行销售安装的，公司会根据地区和市场情况 按需配置的。
# 1.1.7 组件的命名规则
单晶D 多晶P（首字母） 双玻EG 双玻单晶DEG 双玻多晶PEG
PalletNumber:托盘号 ColorCode:组件色系码 S/N：序列号LotNO柜号
X20170809207403车间-年//-流号
托盘：X3517091304361210081C1CF3 组件系数 系有电流分档3档
如：TSM-DEG17MC.20(II) 加个 C 就是双玻双面
# 1.2 逆变器类
"""


    extracted_json = {
  "detected_toc": {
    "raw_text": "# 目录\n# 一、 产品类 .... 3\n# 二、 业务模式和合作类型. 6\n# 三、 商务流程指导.. .17\n# 四、售后类.. 19\n# 五、客服必备常见故障排查... .25\n5.1 离线.. . 26\n5.2 故障.. .. 26\n5.3 低效能.. ...29\n5.4 频繁故障. .29\n5.5 屋顶漏雨. .30\n5.6 房屋修缮. ..30\n5.7 国网数据异常. ..31\n5.8 舆情&客诉. ..... 31\n5.9 故障提醒规则. ...33\n六、疑难问题处理流程和对接话术.. . 35\n6.1 疑难问题处理话术. . 35\n6.2话务派单规则. .. 37\n6.3售后系统操作指导. ..42\n七、联络中心现场工作规范及业务流程指引. ...43\n7.1 现场工作规范. ...43\n7.2 话务坐席客服客服工作指引. .. 45\n7.3微信群对接. ... 45\n7.4工单审核和派单. ...46"
  },
  "new_structure": {
    "联络中心办事指南及常见问题百问百答": {
      "children": {
        "一、 产品类": {
          "children": {
            "1.1 组件类": {
              "children": {
                "1.1.1 组件板上为什么有色差？": {
                  "children": {}
                },
                "1.1.2 组件板上有白色的斑点是什么情况？": {
                  "children": {}
                },
                "1.1.3 组件板的等级是怎么区分？": {
                  "children": {}
                },
                "1.1.4 组件背光度怎么不一样？": {
                  "children": {}
                },
                "1.1.5 光伏组件要定期清洗吗？": {
                  "children": {}
                },
                "1.1.6 你们的产品配置，组件功率是多少的？": {
                  "children": {}
                },
                "1.1.7 组件的命名规则": {
                  "children": {}
                }
              }
            },
            "1.2 逆变器类": {
              "children": {}
            }
          }
        }
      }
    }
  }
}
    results = validate_extracted_structure_by_line(md_text, extracted_json)

    print("\n=== 验证结果 ===\n")
    for r in results:
        print(f"标题: {r['title']}")
        print(f"  ✅ found: {r['found']} | score: {r['match_score']} | line: {r['line_number']}")
        print(f"  匹配行: {r['matched_line']}\n")