#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_docx_styles: 将 pandoc 输出的标题样式映射到 .dotx 模板的自定义样式。

pandoc 写入的 Heading1/Heading2 等标准样式 ID 在某些中文模板中不存在，
导致 Word 回退为 Normal 外观。本脚本在 XML 层面替换样式 ID。

用法:
  python3 fix_docx_styles.py <docx_file> [style_map_json]

style_map_json 格式 (可选，默认使用内置映射):
  {"Heading1":"af9","Heading2":"afb","Heading3":"afd","3":"afd"}
"""

import json
import shutil
import sys
import tempfile
import zipfile
from lxml import etree
from pathlib import Path

# 默认映射：pandoc 样式 ID → 模板样式 ID
DEFAULT_STYLE_MAP = {
    "Heading1": "af9",       # 一级标题
    "Heading2": "afb",       # 二级标题
    "Heading3": "afd",       # 三级标题
    "3": "afd",              # heading 3 → 三级标题
    "AbstractTitle": "af9",  # 摘要标题 → 一级标题
}

WML_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": WML_NS}


def audit_template_styles(template_path: str) -> dict:
    """审计模板中的标题样式，返回 {name: styleId} 映射。"""
    result = {}
    with zipfile.ZipFile(template_path, "r") as z:
        tree = etree.parse(z.open("word/styles.xml"))
    for style in tree.findall(".//w:style", NS):
        sid = style.get(f"{{{WML_NS}}}styleId")
        name_el = style.find("w:name", NS)
        if name_el is None:
            continue
        name = name_el.get(f"{{{WML_NS}}}val")
        if "标题" in name or "heading" in name.lower():
            result[name] = sid
    return result


def fix_styles(input_path: str, output_path: str = None,
               style_map: dict = None):
    """读取 docx，替换 document.xml 中的样式引用。"""
    if output_path is None:
        output_path = input_path
    if style_map is None:
        style_map = DEFAULT_STYLE_MAP

    input_p = Path(input_path)
    replaced = 0

    with zipfile.ZipFile(input_p, "r") as zin:
        tree = etree.parse(zin.open("word/document.xml"))

    body = tree.getroot().find(".//w:body", NS)
    for pStyle in body.iter(f"{{{WML_NS}}}pStyle"):
        val = pStyle.get(f"{{{WML_NS}}}val")
        if val in style_map:
            pStyle.set(f"{{{WML_NS}}}val", style_map[val])
            replaced += 1

    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".docx", dir=input_p.parent
    )
    tmp.close()

    with zipfile.ZipFile(input_p, "r") as zin, \
         zipfile.ZipFile(tmp.name, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == "word/document.xml":
                zout.writestr(
                    item,
                    etree.tostring(tree, xml_declaration=True,
                                   encoding="UTF-8", standalone=True),
                )
            else:
                zout.writestr(item, zin.read(item.filename))

    shutil.move(tmp.name, output_path)
    print(f"已映射 {replaced} 个标题样式")


if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "main_pandoc.docx"
    style_map = DEFAULT_STYLE_MAP
    if len(sys.argv) > 2:
        style_map = json.loads(sys.argv[2])
    output_file = input_file
    fix_styles(input_file, output_file, style_map)
