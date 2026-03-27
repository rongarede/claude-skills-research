---
name: semantic-scholar
description: 使用 Semantic Scholar API 检索和验证学术论文。支持并发多关键词搜索、批量 ID/DOI 查询、引用分析、批量补全摘要、统一 Markdown 导出。覆盖 2.14 亿+ 学术论文，无需 API Key 即可使用。触发词：论文检索、论文验证、Semantic Scholar、S2 搜索、查论文、补全摘要、导出MD
allowed-tools: [Bash, Read, Write, Edit]
---

# Semantic Scholar 论文检索与验证

## 概述

基于 Semantic Scholar Academic Graph API 的论文检索工具，支持：
- **并发搜索**：同时查询多个关键词
- **批量验证**：通过 DOI / ArXiv ID / S2 ID 批量查询论文详情
- **引用分析**：获取引用数、被引论文
- **开放获取**：识别 OA 论文和 PDF 链接

覆盖 214M+ 学术论文，免费无需注册。

## 执行步骤

1. 确认搜索意图：用户提供关键词、DOI 或论文 ID
2. 选择搜索模式：单关键词搜索、多关键词并发搜索、批量 ID 查询
3. 执行搜索脚本 `search_papers.py`，获取结果 JSON
4. 如需摘要补全，执行 `batch_abstract.py` 批量获取缺失摘要
5. 如需格式化输出，执行 `export_md.py` 生成 Markdown 报告
6. 返回结果给用户，附带论文数量和关键统计

## 约束

- **禁止**在无用户确认的情况下自动清除缓存（`--clear-cache`）
- **禁止**将 API Key 硬编码到脚本或 commit 中
- 不可绕过速率限制器直接发请求
- 批量查询每批不可超过 500 篇（API 限制）
- 缓存 TTL 固定 3600s，不可在运行时修改

## 使用场景

- 按关键词检索论文标题、作者、年份
- 验证论文是否存在及其元数据是否正确
- 批量查询一组 DOI 对应的论文信息
- 与 OpenAlex 交叉验证检索结果
- 查找某领域高引论文

## 快速开始

### 依赖安装

```bash
pip install aiohttp
```

### API Key 配置（可选）

无 Key 可用（1 req/s），配置 Key 后提升至 10 req/s。三种配置方式：

```bash
# 方式 1：交互式配置（推荐，保存到配置文件）
python $SCRIPTS/search_papers.py --setup

# 方式 2：环境变量
export S2_API_KEY="your-key-here"

# 方式 3：手动写入配置文件
# ~/.config/semantic-scholar/config.json
# {"api_key": "your-key-here"}
```

Key 解析优先级：`--api-key` 参数 → `S2_API_KEY` 环境变量 → 配置文件

支持两种 Key：
- **官方 Key**：申请地址 https://www.semanticscholar.org/product/api#api-key-form
- **ai4scholar.net 代理 Key**：以 `sk-user-` 开头，自动路由到 ai4scholar.net

### CLI 用法

```bash
SCRIPTS=~/.claude/skills/semantic-scholar/scripts

# 单关键词搜索
python $SCRIPTS/search_papers.py "blockchain consensus"

# 并发多关键词搜索
python $SCRIPTS/search_papers.py "HotStuff BFT" "DAG consensus" "PBFT protocol"

# 按 DOI 批量查询
python $SCRIPTS/search_papers.py --ids "DOI:10.1145/3293611.3331591" "ARXIV:1803.05069"

# 年份 + 引用数过滤
python $SCRIPTS/search_papers.py "consensus algorithm" --year "2020-" --min-cite 50

# 输出到 JSON
python $SCRIPTS/search_papers.py "BFT consensus" -n 20 -o results.json

# 跳过缓存（强制重新请求）
python $SCRIPTS/search_papers.py "HotStuff" --no-cache

# 清除所有缓存
python $SCRIPTS/search_papers.py --clear-cache
```

### Python API 用法

```python
import asyncio
from scripts.s2_client import S2Client

async def main():
    client = S2Client()  # 或 S2Client(api_key="your-key")

    # 单次搜索
    result = await client.search("blockchain consensus", limit=5)
    for p in result["data"]:
        print(f"{p['title']} ({p['year']}) - 引用: {p['citationCount']}")

    # 并发搜索多个关键词
    queries = ["HotStuff BFT", "DAG consensus", "PBFT protocol"]
    results = await client.search_concurrent(queries, limit=5)
    for q, r in results.items():
        print(f"\n== {q} ({r['total']} 条) ==")
        for p in r["data"]:
            print(f"  {p['title']}")

    # 批量 ID 查询
    papers = await client.batch_papers([
        "DOI:10.1145/3293611.3331591",
        "ARXIV:1803.05069",
    ])
    for p in papers:
        if p:
            print(f"{p['title']} ({p['year']})")

    await client.close()

asyncio.run(main())
```

## API 端点

| 端点 | 方法 | 用途 | 限制 |
|------|------|------|------|
| `/paper/search` | GET | 关键词搜索 | 100 条/页, offset ≤ 9999 |
| `/paper/search/bulk` | GET | 大规模搜索 | 1000 条/页, token 分页 |
| `/paper/batch` | POST | 批量 ID 查询 | 500 ID/次 |
| `/paper/{id}` | GET | 单篇详情 | - |

## 支持的论文 ID 格式

| 格式 | 示例 |
|------|------|
| S2 Paper ID | `204e3073870fae3d05bcbc2f6a8e263d9b72e776` |
| DOI | `DOI:10.1145/3293611.3331591` |
| ArXiv | `ARXIV:1803.05069` |
| Corpus ID | `CorpusId:13756489` |
| PubMed | `PMID:12345678` |
| ACL | `ACL:P18-1234` |

## 返回字段

### 基础字段 (DEFAULT_FIELDS)
`title, authors, year, citationCount, externalIds, venue`

### 详细字段 (DETAIL_FIELDS)
`title, authors, year, citationCount, externalIds, venue, abstract, referenceCount, isOpenAccess, openAccessPdf`

## 速率限制

| 模式 | 速率 | 日限额 |
|------|------|--------|
| 无 Key | 1 req/s | 5000/5min |
| 有 Key | 10 req/s | 无硬限制 |

内置 Semaphore(5) 并发控制 + 令牌桶速率限制，防止瞬间打满。

## 与 OpenAlex 交叉验证

```python
# 1. 用 OpenAlex 搜索
openalex_results = openalex_client.search_works(search="HotStuff BFT")

# 2. 提取 DOI 列表
dois = [f"DOI:{w['doi'].split('doi.org/')[-1]}"
        for w in openalex_results if w.get('doi')]

# 3. 用 Semantic Scholar 批量验证
s2_papers = await s2_client.batch_papers(dois)

# 4. 对比标题、年份、引用数
for oa, s2 in zip(openalex_results, s2_papers):
    if s2:
        match = oa['title'].lower() == s2['title'].lower()
        print(f"{'✓' if match else '✗'} {oa['title']}")
```

## 脚本说明

### file_utils.py
共享文件查找工具：
- `find_json_files()` — 从路径参数解析 `layer_*_raw.json` 文件（支持目录和单文件）
- 被 `batch_abstract.py` 和 `export_md.py` 共同引用，消除重复代码

### s2_client.py
异步 API 客户端，核心功能：
- `search()` — 单次关键词搜索（带磁盘缓存）
- `search_concurrent()` — 并发多关键词搜索（Semaphore 控制并发度）
- `batch_papers()` — 批量 ID 查询（自动分批，每批 500）
- `paper_detail()` — 单篇详情
- `bulk_search()` — 大规模搜索（token 分页）
- 内置令牌桶速率限制 + 指数退避重试 + Semaphore(5) 并发控制
- Key 解析链：显式参数 → 环境变量 → 配置文件
- 磁盘缓存（SHA256 hash，TTL 3600s）

### search_papers.py
CLI 搜索工具：
- 支持多关键词并发
- 支持 `--ids` 批量查询
- 支持 `--year`、`--min-cite` 过滤
- `--setup` 交互式配置 API Key
- `--no-cache` 跳过缓存
- `--clear-cache` 清除所有缓存
- 输出格式化文本或 JSON

### batch_abstract.py
批量补全搜索结果中缺失的摘要：
- 读取 `layer_*_raw.json` 文件，提取缺少 `abstract` 的 paperId
- 通过 `S2Client.batch_papers()` 批量获取摘要
- 写回原 JSON 文件（追加 `abstract` 字段）
- 支持 `--dry-run` 仅检查不请求

```bash
SCRIPTS=~/.claude/skills/semantic-scholar/scripts

# 补全指定目录下所有 layer_*_raw.json 的摘要
python $SCRIPTS/batch_abstract.py /path/to/results/

# 补全指定文件
python $SCRIPTS/batch_abstract.py layer_1_raw.json layer_2_raw.json

# 仅检查缺失情况
python $SCRIPTS/batch_abstract.py /path/to/results/ --dry-run
```

### export_md.py
从 raw JSON 生成统一格式的 Markdown 文件：
- 统一输出格式：标题 → 搜索主题 → 论文列表表格 → 详细内容（含摘要）
- 自动从文件名提取 layer 编号，匹配中文标题
- 支持 `--titles` 自定义标题映射

```bash
SCRIPTS=~/.claude/skills/semantic-scholar/scripts

# 导出指定目录下所有 layer → Markdown
python $SCRIPTS/export_md.py /path/to/results/

# 自定义 layer 标题
python $SCRIPTS/export_md.py /path/to/results/ --titles '{"1":"综述","2":"信誉"}'
```

**典型工作流（搜索 → 补全摘要 → 导出 Markdown）：**

```bash
SCRIPTS=~/.claude/skills/semantic-scholar/scripts

# 1. 搜索并保存 raw JSON
python $SCRIPTS/search_papers.py "HotStuff BFT" "DAG consensus" -n 15 --year "2020-" -o layer_8_raw.json

# 2. 补全摘要
python $SCRIPTS/batch_abstract.py layer_8_raw.json

# 3. 导出统一格式 Markdown
python $SCRIPTS/export_md.py layer_8_raw.json
```

## 配置文件

配置文件位于 `~/.config/semantic-scholar/config.json`：

```json
{
  "api_key": "your-key-here"
}
```

缓存目录：`~/.config/semantic-scholar/cache/`
