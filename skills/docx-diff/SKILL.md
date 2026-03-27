---
name: docx-diff
description: "对比两份 DOCX 文件的格式差异（styles/numbering/theme），输出 JSON。触发词：/docx-diff、对比 docx、Word 格式对比、比较两份 Word、docx 差异"
---

# DOCX Format Diff

对比两份 Word 文档的格式级差异，输出结构化 JSON。

## 用法

```bash
python3 ~/.claude/skills/docx-diff/scripts/docx_format_diff.py \
    <docx_a> <docx_b> [--output <file.json>] [--sections styles,numbering,theme]
```

## 参数

| 参数 | 说明 |
|------|------|
| `docx_a` | 第一份 DOCX 路径（必需） |
| `docx_b` | 第二份 DOCX 路径（必需） |
| `--output` | JSON 输出文件路径（默认 stdout） |
| `--sections` | 比较哪些部分，逗号分隔（默认 `styles,numbering,theme`） |

## 输出结构

```json
{
  "meta": { "file_a": "...", "file_b": "...", "timestamp": "...", "sections_compared": [...] },
  "styles": { "only_in_a": [...], "only_in_b": [...], "differences": [...] },
  "numbering": { "abstract_nums": { "only_in_a": [...], "only_in_b": [...], "differences": [...] } },
  "theme": { "major_font": { "a": "...", "b": "..." }, "minor_font": { "a": "...", "b": "..." } }
}
```

## 比较维度

- **styles**: styles.xml 中所有 `w:style` 的段落属性(pPr)、run 属性(rPr)、表格属性(tblPr)
- **numbering**: numbering.xml 中 `w:abstractNum` 的级别定义(numFmt, lvlText, indent)
- **theme**: theme/theme1.xml 中 majorFont/minorFont 的 latin 和 ea 字体
