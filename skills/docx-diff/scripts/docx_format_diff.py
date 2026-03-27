#!/usr/bin/env python3
"""Compare formatting differences between two DOCX files.

Compares styles.xml, numbering.xml, and theme/theme1.xml at the style level,
outputting a structured JSON report.

Usage:
    python3 docx_format_diff.py <docx_a> <docx_b> [--output file.json] [--sections styles,numbering,theme]
"""

import argparse
import json
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

# OOXML 命名空间
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
NS = {"w": W_NS, "a": A_NS}


def _qn(ns_prefix: str, local: str) -> str:
    """构建命名空间限定的元素/属性名。"""
    return f"{{{NS[ns_prefix]}}}{local}"


def _extract_xml(docx_path: str, xml_path: str) -> ET.Element | None:
    """从 DOCX ZIP 中提取并解析 XML 文件。"""
    try:
        with zipfile.ZipFile(docx_path) as z:
            if xml_path not in z.namelist():
                return None
            return ET.parse(z.open(xml_path)).getroot()
    except (zipfile.BadZipFile, KeyError):
        return None


# ── styles.xml 比较 ──────────────────────────────────────────────


def _elem_to_dict(el: ET.Element) -> dict:
    """将 XML 元素的子元素展平为 {localTag: value} 字典。"""
    result = {}
    for child in el:
        tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
        # 优先取 w:val 风格属性
        val = child.get(_qn("w", "val")) or child.get("val") or child.get(_qn("w", "w"))
        if val is not None:
            result[tag] = val
        else:
            # 收集所有属性为子字典
            attrs = {k.split("}")[-1]: v for k, v in child.attrib.items()}
            if attrs:
                result[tag] = attrs
            elif child.text and child.text.strip():
                result[tag] = child.text.strip()
    return result


def _compare_prop_groups(
    el_a: ET.Element | None, el_b: ET.Element | None, group_name: str
) -> list[dict]:
    """比较两个属性组元素 (pPr, rPr, tblPr)，返回差异列表。"""
    diffs = []
    dict_a = _elem_to_dict(el_a) if el_a is not None else {}
    dict_b = _elem_to_dict(el_b) if el_b is not None else {}
    all_keys = sorted(set(dict_a) | set(dict_b))
    for key in all_keys:
        va = dict_a.get(key)
        vb = dict_b.get(key)
        if va != vb:
            diffs.append({
                "path": f"{group_name}/{key}",
                "a": va if va is not None else None,
                "b": vb if vb is not None else None,
            })
    return diffs


def _compare_styles(root_a: ET.Element | None, root_b: ET.Element | None) -> dict:
    """比较两份 DOCX 的 styles.xml。"""
    if root_a is None and root_b is None:
        return {"only_in_a": [], "only_in_b": [], "differences": []}

    def _index_styles(root):
        styles = {}
        if root is None:
            return styles
        for s in root.findall("w:style", NS):
            sid = s.get(_qn("w", "styleId"))
            if sid:
                styles[sid] = s
        return styles

    styles_a = _index_styles(root_a)
    styles_b = _index_styles(root_b)

    ids_a = set(styles_a)
    ids_b = set(styles_b)

    only_a = sorted(ids_a - ids_b)
    only_b = sorted(ids_b - ids_a)

    differences = []
    for sid in sorted(ids_a & ids_b):
        sa = styles_a[sid]
        sb = styles_b[sid]
        name_el = sa.find("w:name", NS)
        style_name = name_el.get(_qn("w", "val"), "") if name_el is not None else ""

        props = []
        for group in ("pPr", "rPr", "tblPr"):
            ga = sa.find(f"w:{group}", NS)
            gb = sb.find(f"w:{group}", NS)
            if ga is not None or gb is not None:
                props.extend(_compare_prop_groups(ga, gb, group))

        # 比较 basedOn
        ba_a = sa.find("w:basedOn", NS)
        ba_b = sb.find("w:basedOn", NS)
        val_a = ba_a.get(_qn("w", "val")) if ba_a is not None else None
        val_b = ba_b.get(_qn("w", "val")) if ba_b is not None else None
        if val_a != val_b:
            props.append({"path": "basedOn", "a": val_a, "b": val_b})

        if props:
            differences.append({
                "style_id": sid,
                "style_name": style_name,
                "properties": props,
            })

    return {"only_in_a": only_a, "only_in_b": only_b, "differences": differences}


# ── numbering.xml 比较 ──────────────────────────────────────────


def _compare_numbering(root_a: ET.Element | None, root_b: ET.Element | None) -> dict:
    """比较两份 DOCX 的 numbering.xml。"""
    if root_a is None and root_b is None:
        return {"abstract_nums": {"only_in_a": [], "only_in_b": [], "differences": []}}

    def _index_abstract_nums(root):
        nums = {}
        if root is None:
            return nums
        for an in root.findall("w:abstractNum", NS):
            aid = an.get(_qn("w", "abstractNumId"))
            if aid:
                nums[aid] = an
        return nums

    def _level_to_dict(lvl: ET.Element) -> dict:
        result = {}
        for child in lvl:
            tag = child.tag.split("}")[-1] if "}" in child.tag else child.tag
            val = child.get(_qn("w", "val"))
            if val is not None:
                result[tag] = val
            else:
                attrs = {k.split("}")[-1]: v for k, v in child.attrib.items()}
                if attrs:
                    result[tag] = attrs
        return result

    nums_a = _index_abstract_nums(root_a)
    nums_b = _index_abstract_nums(root_b)

    ids_a = set(nums_a)
    ids_b = set(nums_b)

    only_a = sorted(ids_a - ids_b, key=lambda x: int(x))
    only_b = sorted(ids_b - ids_a, key=lambda x: int(x))

    differences = []
    for aid in sorted(ids_a & ids_b, key=lambda x: int(x)):
        an_a = nums_a[aid]
        an_b = nums_b[aid]
        lvls_a = {l.get(_qn("w", "ilvl")): l for l in an_a.findall("w:lvl", NS)}
        lvls_b = {l.get(_qn("w", "ilvl")): l for l in an_b.findall("w:lvl", NS)}
        all_ilvls = sorted(set(lvls_a) | set(lvls_b))
        level_diffs = []
        for ilvl in all_ilvls:
            da = _level_to_dict(lvls_a[ilvl]) if ilvl in lvls_a else {}
            db = _level_to_dict(lvls_b[ilvl]) if ilvl in lvls_b else {}
            all_keys = sorted(set(da) | set(db))
            for key in all_keys:
                if da.get(key) != db.get(key):
                    level_diffs.append({
                        "level": ilvl,
                        "property": key,
                        "a": da.get(key),
                        "b": db.get(key),
                    })
        if level_diffs:
            differences.append({"abstractNumId": aid, "levels": level_diffs})

    return {
        "abstract_nums": {
            "only_in_a": only_a,
            "only_in_b": only_b,
            "differences": differences,
        }
    }


# ── theme/theme1.xml 比较 ───────────────────────────────────────


def _compare_theme(root_a: ET.Element | None, root_b: ET.Element | None) -> dict:
    """比较两份 DOCX 的 theme/theme1.xml 字体定义。"""

    def _get_fonts(root):
        if root is None:
            return {"major": {}, "minor": {}}
        result = {}
        for kind in ("major", "minor"):
            el = root.find(f".//a:{kind}Font", NS)
            if el is None:
                result[kind] = {}
                continue
            fonts = {}
            for child_tag in ("latin", "ea", "cs"):
                child = el.find(f"a:{child_tag}", NS)
                if child is not None:
                    fonts[child_tag] = child.get("typeface", "")
            result[kind] = fonts
        return result

    fonts_a = _get_fonts(root_a)
    fonts_b = _get_fonts(root_b)

    result = {}
    for kind in ("major_font", "minor_font"):
        key = kind.replace("_font", "")
        fa = fonts_a.get(key, {})
        fb = fonts_b.get(key, {})
        entry = {}
        for attr in sorted(set(fa) | set(fb)):
            va = fa.get(attr, "")
            vb = fb.get(attr, "")
            if va != vb:
                entry[attr] = {"a": va, "b": vb}
        if entry:
            result[kind] = entry

    return result


# ── CLI 入口 ────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="对比两份 DOCX 文件的格式差异（styles/numbering/theme），输出 JSON。"
    )
    parser.add_argument("docx_a", help="第一份 DOCX 路径")
    parser.add_argument("docx_b", help="第二份 DOCX 路径")
    parser.add_argument("--output", "-o", help="JSON 输出文件路径（默认 stdout）")
    parser.add_argument(
        "--sections",
        "-s",
        default="styles,numbering,theme",
        help="逗号分隔的比较部分（默认 styles,numbering,theme）",
    )
    args = parser.parse_args()

    for path in (args.docx_a, args.docx_b):
        if not Path(path).is_file():
            print(f"错误: 文件不存在: {path}", file=sys.stderr)
            sys.exit(1)

    sections = [s.strip() for s in args.sections.split(",")]

    result = {
        "meta": {
            "file_a": Path(args.docx_a).name,
            "file_b": Path(args.docx_b).name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "sections_compared": sections,
        }
    }

    if "styles" in sections:
        sa = _extract_xml(args.docx_a, "word/styles.xml")
        sb = _extract_xml(args.docx_b, "word/styles.xml")
        result["styles"] = _compare_styles(sa, sb)

    if "numbering" in sections:
        na = _extract_xml(args.docx_a, "word/numbering.xml")
        nb = _extract_xml(args.docx_b, "word/numbering.xml")
        result["numbering"] = _compare_numbering(na, nb)

    if "theme" in sections:
        ta = _extract_xml(args.docx_a, "word/theme/theme1.xml")
        tb = _extract_xml(args.docx_b, "word/theme/theme1.xml")
        result["theme"] = _compare_theme(ta, tb)

    output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"已写入 {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == "__main__":
    main()
