---
name: academic-paper-pipeline
description: |
  学术文献端到端检索管线：关键词矩阵设计→多路并行检索→PDF下载→段落提取→主题分组合并。
  触发词：/paper-pipeline、学术检索管线、论文批量检索、文献检索管线
---

# Academic Paper Pipeline

学术文献端到端检索管线。从关键词设计到原文段落提取，一站式完成。

## 触发方式

- `/paper-pipeline`
- 「学术检索管线」「论文批量检索」「文献检索管线」
- 用户要求对某主题进行大规模文献检索时

## 工作流程

### Phase 1: 关键词矩阵设计

与用户确认：
1. **检索目标**：改写参考 / 内容扩充 / 术语校准 / 全面覆盖
2. **数据源范围**：学术论文 / +工程文档 / +中文论文 / 全覆盖
3. **深度**：宽而浅(50+篇×摘要) / 中等(20-30篇×段落) / 窄而深(10-15篇×完整章节)
4. **输出格式**：按主题分组 / 按论文分组 / 对比矩阵

设计 N 维关键词矩阵（通常 4-8 维），每维 3-5 个查询串。

### Phase 2: 多路并行检索

按数据源拆分为 N 个并行 agent：

| Agent | 数据源 | 工具 |
|-------|--------|------|
| yomi（主力） | Semantic Scholar | semantic-scholar skill |
| Lyric/Astra | arXiv 预印本 | WebSearch site:arxiv.org + WebFetch |
| Cipher/Nexus | IEEE/ACM + 中文 | WebSearch site:ieeexplore.ieee.org + 中文关键词 |

**规则：**
- 最少 2 路并行，最多 5 路
- 每路写入独立原始文件（`raw_{source}.md`）
- 所有 agent 完成后 UNION 合并去重

### Phase 3: PDF 下载

2 路并行下载 agent：

| Agent | 来源 | 方法 |
|-------|------|------|
| tetsu-arXiv | arXiv 论文 | `curl -L https://arxiv.org/pdf/{id}.pdf` |
| tetsu-DOI | 非 arXiv 论文 | sci-hub-download skill (OA → Sci-Hub → publisher) |

**输出：**
- PDF 存入 `<output_dir>/papers/`
- 创建 `download_log.md` 记录成功/失败
- 验证：PDF > 100KB 视为有效

### Phase 4: 并行 PDF 段落提取

将下载的 PDF 按文件名字母序分为 N 批（每批 ~10 篇），并行读取：

| Agent | 文件范围 | 输出 |
|-------|---------|------|
| reader-1 | A-E | `extracts/batch1.md` |
| reader-2 | F-J | `extracts/batch2.md` |
| reader-3 | K-O | `extracts/batch3.md` |
| reader-4 | P-T | `extracts/batch4.md` |
| reader-5 | U-Z+数字 | `extracts/batch5.md` |

**每篇 PDF 读取规则：**
- 用 Read 工具的 `pages` 参数分批读取（每次 ≤20 页）
- 优先读取 Introduction、Protocol、View Change、Recovery 等关键章节
- 提取包含关键词的完整段落（≥3 句上下文）
- 记录：页码、章节标题、段落原文

### Phase 5: 主题分组合并

1. 合并所有 batch 提取文件
2. 按预设主题重新分组
3. 每篇论文标准格式：

```
### [Author, Year] Title
- **来源**: 会议/期刊, DOI/arXiv ID
- **相关段落**: "..."（原文）
- **表述模式**: [定性描述/形式化定义/流程叙述/对比分析]
- **可借鉴点**: ...
```

4. 附录：术语对照表
5. 统计摘要：总论文数、按主题分布、按年份分布

## 目录结构

```
<output_dir>/research/<topic>/
├── 2026-MM-DD-<topic>-research.md  # 最终合并报告
├── raw_S2.md                        # Semantic Scholar 原始结果
├── raw_arXiv.md                     # arXiv 原始结果
├── raw_IEEE.md                      # IEEE/ACM 原始结果
├── papers/                          # 下载的 PDF
│   ├── paper1.pdf
│   ├── download_log.md
│   └── ...
└── extracts/                        # PDF 段落提取
    ├── batch1.md
    ├── batch2.md
    └── ...
```

## 管线执行规则

1. **Phase 2 规划完后自动推进所有后续 Phase**——不逐步等用户确认
2. Phase 间的数据依赖：Phase 3 依赖 Phase 2 的论文列表，Phase 4 依赖 Phase 3 的 PDF
3. 无依赖的 Phase 内步骤尽量并行
4. 每个 Phase 完成后更新任务面板状态

## Anti-Patterns

- 单 agent 串行检索所有数据源
- 只检索摘要不下载 PDF
- 只下载 PDF 不提取段落
- 逐步等用户催促而非管线自动推进
- Phase 3 跳过 sci-hub（会漏掉 IEEE/ACM 论文）
