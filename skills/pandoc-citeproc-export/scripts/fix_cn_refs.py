#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""后处理 pandoc 导出的 docx，区分中英文参考文献格式。

中文条目规则（与英文的差异）：
  - et al. → 等
  - 作者间逗号后无空格：肖恒辉,李炯城
  - 标题与类型标识间无空格：研究[J]
  - 类型标识后句点与期刊名间无空格：[J].电信科学
  - 卷号与期号间无空格：29(01)
  - 结尾使用半角句点 .
"""

import re
import sys
from pathlib import Path
from docx import Document


def has_chinese(text: str) -> bool:
    """检测文本是否包含中文字符。"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def is_chinese_ref(para_text: str) -> bool:
    """判断参考文献条目是否为中文（基于作者区域）。"""
    # 提取 [N] 之后、第一个 . 之前的作者区域
    m = re.match(r'\[\d+\]\s*(.+?)(?:\.|\[)', para_text)
    if m:
        return has_chinese(m.group(1))
    return has_chinese(para_text[:40])


def fix_chinese_ref(text: str) -> str:
    """对中文参考文献条目应用格式修正。"""
    # 1. et al. → 等.（保留句点）
    text = re.sub(r',\s*et al\.', ',等.', text)

    # 2. 中文作者间逗号后去空格（仅中文字符之间）
    text = re.sub(r'([\u4e00-\u9fff]),\s+([\u4e00-\u9fff])', r'\1,\2', text)

    # 3. 等. 后去空格（等.标题）
    text = re.sub(r'(等)\.\s+', r'\1.', text)

    # 4. 标题与 [J]/[C]/[D] 等之间去空格
    text = re.sub(r'\s+(\[[A-Z]+\])', r'\1', text)

    # 5. [J]. 后去空格
    text = re.sub(r'(\[[A-Z]+\])\.\s+', r'\1.', text)

    # 6. 卷号与期号间去空格：29 (01) → 29(01)
    text = re.sub(r'(\d)\s+\((\d)', r'\1(\2', text)

    # 7. 结尾全角句点 → 半角
    if text.endswith('．'):
        text = text[:-1] + '.'

    return text


def process_docx(input_path: str, output_path: str = None):
    """处理 docx 文件中的参考文献。"""
    if output_path is None:
        output_path = input_path

    doc = Document(input_path)
    ref_started = False
    fixed_count = 0

    for para in doc.paragraphs:
        full_text = para.text.strip()

        # 检测参考文献区域（以 [1] 开头的段落）
        if re.match(r'^\[\d+\]', full_text):
            ref_started = True

        if not ref_started:
            continue

        # 跳过非参考文献段落
        if not re.match(r'^\[\d+\]', full_text):
            continue

        # 仅处理中文条目
        if not is_chinese_ref(full_text):
            continue

        # 对每个 run 应用修正
        # 先拼接所有 run 文本，修正后重新分配
        original = ''.join(run.text for run in para.runs)
        fixed = fix_chinese_ref(original)

        if original != fixed:
            # 将修正后的文本写回第一个 run，清空其余 run
            if para.runs:
                para.runs[0].text = fixed
                for run in para.runs[1:]:
                    run.text = ''
            fixed_count += 1

    doc.save(output_path)
    print(f'已修正 {fixed_count} 条中文参考文献')


if __name__ == '__main__':
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'main_pandoc.docx'
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file
    process_docx(input_file, output_file)
