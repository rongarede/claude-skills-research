---
name: word-to-tex
description: "Word 文本转 LaTeX 工具：将从 Word 复制的内容整理为标准 LaTeX 格式并保存到文件。触发词：/wordtotex、Word转LaTeX、转换为TeX"
---

# Word 转 LaTeX 工具

将从 Word 复制的内容转换为标准 LaTeX 格式并保存到文件。

## 触发方式

- `/wordtotex <filename.tex> [待转换内容]`
- 「把这段 Word 内容转成 LaTeX」
- 「转换为 TeX 格式」

## 输入格式

```
/wordtotex <filename.tex> [待转换内容]
```

## 处理逻辑

1. 从输入中解析出目标文件名 `<filename.tex>`
2. 将后续内容按转换规则转换为 LaTeX 格式
3. 使用文件写入工具将生成的 LaTeX 代码保存到指定文件

## 转换规则

### 标题级次
自动识别并使用对应的 LaTeX 命令：
- 一级标题 → `\section{}`
- 二级标题 → `\subsection{}`
- 三级标题 → `\subsubsection{}`

### 数学公式
- 行内公式：`$...$`
- 独立公式：`equation` 环境

```latex
% 行内
The formula $E = mc^2$ is famous.

% 独立
\begin{equation}
    E = mc^2
\end{equation}
```

### 列表环境
- 无序列表 → `itemize`
- 有序列表 → `enumerate`

```latex
\begin{itemize}
    \item First item
    \item Second item
\end{itemize}

\begin{enumerate}
    \item First item
    \item Second item
\end{enumerate}
```

### 特殊字符转义
必须正确转义以下字符：

| 字符 | 转义形式 |
|------|----------|
| & | `\&` |
| % | `\%` |
| $ | `\$` |
| _ | `\_` |
| # | `\#` |
| { | `\{` |
| } | `\}` |
| ~ | `\textasciitilde` |
| ^ | `\textasciicircum` |
| \ | `\textbackslash` |

## 核心要求

- **纯净输出**：写入文件的内容仅包含 LaTeX 代码，不含 Markdown 标记
- **静默执行**：不在终端输出转换结果预览，仅通过工具完成
- **文件写入**：必须使用 Write 工具将结果保存到指定文件

## 示例

**输入**：
```
/wordtotex intro.tex

1. Introduction

This paper presents a novel approach to distributed consensus.
The key contribution includes:
• Improved throughput
• Lower latency
• Better fault tolerance

The formula E = mc² demonstrates the relationship.
```

**输出文件 `intro.tex`**：
```latex
\section{Introduction}

This paper presents a novel approach to distributed consensus.
The key contribution includes:
\begin{itemize}
    \item Improved throughput
    \item Lower latency
    \item Better fault tolerance
\end{itemize}

The formula $E = mc^2$ demonstrates the relationship.
```
