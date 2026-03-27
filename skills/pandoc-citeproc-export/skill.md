---
name: pandoc-citeproc-export
description: "LaTeX 工程通过 pandoc + citeproc 导出为 Word (.docx)，保留 GB/T 7714-2015 引用格式并区分中英文。触发词：/pandoc-export、pandoc导出、LaTeX转Word、导出docx引用"
---

# Pandoc Citeproc Export

将 biblatex LaTeX 工程导出为带正确引用格式的 Word 文档。

## 触发方式

- `/pandoc-export`
- 「把 LaTeX 导出为 Word」
- 「pandoc 导出 docx」
- 「导出带引用的 docx」

## 适用场景

- LaTeX 工程使用 biblatex + biber 管理参考文献
- 需要导出为 .docx 且保留 [1][2] 编号引用格式
- 需要区分中英文参考文献格式（中文用「等」，英文用 et al.）

## 前置检查清单

导出前必须逐项验证：

| 检查项 | 命令 | 通过条件 |
|--------|------|----------|
| CSL 文件存在 | `ls *.csl` | 存在 gb7714-2015-numeric.csl |
| bib 文件存在 | `ls *.bib` | 存在且非空 |
| 引用键匹配 | 见下方脚本 | tex 中所有 `\cite{}` 键在 bib 中有定义 |
| bib 条目类型 | 见下方脚本 | 有 `booktitle` 的条目应为 `@inproceedings` |
| 模板文件 | `ls *.dotx` | reference-doc 模板存在 |
| 模板标题样式 | 见下方审计 | 确认模板中 heading 1/2 是否存在 |

### 引用键校验脚本

```bash
bash ~/.claude/skills/pandoc-citeproc-export/scripts/check_refs.sh
```

### 模板标题样式审计

许多中文 .dotx 模板不定义标准 `heading 1` / `heading 2`，而使用自定义样式名（如「一级标题」「二级标题」）。pandoc 写入的 `Heading1`/`Heading2` 在模板中找不到定义时，Word 会回退为 Normal 外观。

**审计方法**：用 `fix_docx_styles.py` 的 `audit_template_styles()` 函数扫描模板：

```python
from fix_docx_styles import audit_template_styles
print(audit_template_styles("template.dotx"))
# 输出示例: {'一级标题': 'af9', '二级标题': 'afb', '三级标题': 'afd', 'heading 3': '3'}
```

若模板缺少 `heading 1` / `heading 2`，则必须配置样式映射（见步骤 2）。

## 执行流程

### 步骤 1：导出

```bash
bash ~/.claude/skills/pandoc-citeproc-export/scripts/export.sh \
  --tex main.tex \
  --bib refs.bib \
  --csl gb7714-2015-numeric.csl \
  --ref-doc template.dotx \
  --output main_pandoc.docx
```

export.sh 内部自动执行步骤 2-4，也可手动分步执行：

### 步骤 2：标题样式映射

将 pandoc 写入的标准 Heading 样式 ID 替换为模板的自定义样式 ID。

```bash
python3 ~/.claude/skills/pandoc-citeproc-export/scripts/fix_docx_styles.py main_pandoc.docx
```

默认映射表（适用于常见中文学术模板）：

| pandoc 写入 | 映射到 | 模板样式名 |
|------------|--------|-----------|
| `Heading1` | `af9` | 一级标题 |
| `Heading2` | `afb` | 二级标题 |
| `Heading3` / `3` | `afd` | 三级标题 |
| `AbstractTitle` | `af9` | 一级标题 |

自定义映射（当模板样式 ID 不同时）：

```bash
python3 fix_docx_styles.py main_pandoc.docx '{"Heading1":"custom1","Heading2":"custom2"}'
```

### 步骤 3：中英文后处理

```bash
python3 ~/.claude/skills/pandoc-citeproc-export/scripts/fix_cn_refs.py main_pandoc.docx
```

### 步骤 4：验证

用 pandoc 提取纯文本，检查引用格式：

```bash
pandoc main_pandoc.docx -t plain 2>/dev/null | grep -E '^\[[0-9]+\]'
```

## CSL 定制规则

GB/T 7714-2015 顺序编码制的 CSL 需要以下定制（相对于官方版本）：

| 规则 | CSL 属性/位置 | 值 |
|------|--------------|-----|
| 作者缩写加句点 | `initialize-with` | `"."` |
| 标题与类型标识间加空格 | type-id group prefix | `" ["` |
| 出处项无空格分隔 | container-periodical delimiter | `","` |
| 页码前无空格 | page delimiter | `":"` |
| 卷号与期号间加空格 | issue prefix | `" ("` |
| 不输出 DOI/URL | access macro | 清空 |
| 不输出 /OL 后缀 | medium-id macro | 仅保留 medium 变量 |
| 结尾全角句点 | layout suffix | `"．"` |
| et al. 术语 | locale terms | `et al.` |

## 中英文差异（后处理规则）

| 项目 | 英文 | 中文 |
|------|------|------|
| 截断术语 | et al. | 等 |
| 作者分隔 | `KUMAR S., LI G.` | `肖恒辉,李炯城` |
| 类型标识前 | `security [J]` | `研究[J]` |
| 类型标识后 | `[J]. IEEE` | `[J].电信科学` |
| 卷期间距 | `35 (4)` | `29(01)` |
| 结尾标点 | `．`（全角） | `.`（半角） |

## 依赖

- pandoc (>= 2.11，支持 --citeproc)
- python3 + python-docx + lxml
- CSL 文件：从 citation-style-language/styles 仓库获取
