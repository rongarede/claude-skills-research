---
name: pdf2md-academic
description: "学术 PDF 转 Markdown 工具：将含公式、图表、引用的学术论文 PDF 转换为排版整洁的 Markdown。触发词：/pdf2md、PDF转Markdown、论文转MD"
---

# 学术 PDF 转 Markdown 工具

将学术类 PDF（含数学公式、图表引用、参考文献）转换为排版整洁、渲染友好的 Markdown，保留论文结构与内容准确性。

## 触发方式

- `/pdf2md <PDF路径>`
- 「把这个 PDF 转成 Markdown」
- 「论文转 MD」

## 输入

- `{PDF路径}` - 学术论文 PDF 文件路径

## 输出

- 仅输出最终 Markdown 内容，不分步提问
- 直接写入文件或输出到终端

## 执行规范

### 1. 结构完整性

保留以下所有部分：
- 标题
- 作者
- 摘要
- 关键词
- 正文各级标题
- 结论
- 参考文献

### 2. 数学公式

| 类型 | 格式 |
|------|------|
| 行内公式 | `$...$` |
| 独立公式 | `$$...$$` |

**要求**：
- 公式语义必须准确
- 变量符号不随意改写
- 确保 `$` 成对闭合

### 3. 段落排版

- 以"其中"或"where"开头的解释段落，首行缩进 2 个空格
- 可使用直接空格或 `&nbsp;&nbsp;`

### 4. 引用与文献

**正文引用格式**：
```latex
\cite{ref1}
\cite{ref1,ref3}
```

**禁止使用**：
- `[n]` 形式
- `\cite{}` 之外的任何格式

**参考文献格式**：
- 每条使用 `\cite{refn}` 对应编号
- 每条之间**必须空一行**，防止合并渲染

### 5. 图表处理

- 无法识别的图像保留占位符
- 添加简短图注说明
- 格式：`[图 X: 图注说明]`

### 6. 算法标准化

**标题格式**：
```markdown
**Algorithm [编号]: [算法名称]**
```

**必须包含**：
- `**Input:**` 输入说明
- `**Output:**` 输出说明

**伪代码格式**：
```pseudo
INPUT: ...
OUTPUT: ...

FOR each item IN collection DO
    IF condition THEN
        # 注释说明
        action()
    ELSE
        other_action()
    END IF
END FOR
RETURN result
```

**代码规范**：
- 用 ` ```pseudo ` 包裹
- 代码块内缩进 4 空格
- 控制流起止对齐
- 关键字全大写：`IF/ELSE/WHILE/FOR/RETURN/INPUT/OUTPUT`
- 变量/函数保留原始大小写
- 注释以 `#` 开头并对齐

### 7. 罗马数字列表格式化

将连续罗马数字编号转换为 Markdown 列表：

**原文**：
```
(i) First item description
(ii) Second item description
```

**转换后**：
```markdown
- **(i) First item:** description.
- **(ii) Second item:** description.
```

**规则**：
- 格式：`- **(编号) 核心术语:** 解释文本...`
- 末尾无句号则补 `.`
- 冒号后首字母按英文习惯（通常小写，专有名词除外）
- 不改原文措辞，仅调整排版与标点

## 执行命令

使用 OCR 读取并转换 PDF：

```
请使用 OCR 读取并转换文件 {PDF路径} 为 Markdown。
输出最终 Markdown，不分步询问。
```

## 自检清单

执行完成后检查：

- [ ] 公式 `$` 是否成对闭合
- [ ] 是否仍有 `[n]` 形式引用（应改为 `\cite{refn}`）
- [ ] "其中/where"段落是否首行缩进 2 空格
- [ ] 参考文献条目之间是否空行
- [ ] 算法是否包含 Input/Output
- [ ] 罗马数字列表是否已格式化

## 输出示例

```markdown
# 论文标题

**作者**: Author Name

## Abstract

摘要内容...

## 1. Introduction

正文内容，引用示例 \cite{ref1}。

公式示例：
$$E = mc^2$$

  其中 $E$ 表示能量，$m$ 表示质量，$c$ 表示光速。

## 2. Related Work

相关工作描述 \cite{ref2,ref3}...

## 3. Method

**Algorithm 1: Example Algorithm**

**Input:** Input description
**Output:** Output description

```pseudo
FOR i = 1 TO n DO
    IF condition THEN
        process(i)
    END IF
END FOR
RETURN result
```

## References

\cite{ref1} Author A. Title of Paper A. *Journal*, 2024.

\cite{ref2} Author B. Title of Paper B. *Conference*, 2023.
```
