---
name: rename-pdf
description: "自动重命名PDF文件：提取PDF元数据标题，清理非法字符，静默重命名。触发词：/renamepdf、重命名PDF、PDF改名"
---

# PDF 自动重命名工具

根据 PDF 元数据标题自动重命名文件。

## 触发方式

- `/renamepdf <PDF文件路径>`
- 「重命名这个 PDF」
- 「用标题重命名 PDF」

## 执行脚本

```bash
bash ~/.claude/skills/rename-pdf/scripts/rename.sh "<PDF文件路径>"
```

## 功能说明

| 功能 | 说明 |
|------|------|
| 提取标题 | 从 PDF 元数据 Title 字段获取 |
| 清理字符 | 将 `/ \ : * ? " < > |` 替换为 `-` |
| 静默执行 | 直接重命名，仅输出结果 |

## 依赖

- `exiftool` 或 `pdfinfo`（二选一）

## 示例

**输入**：
```
/renamepdf /Users/bit/Downloads/paper.pdf
```

**输出**：
```
✓ 已重命名为: A Novel Approach to BFT Consensus.pdf
```
