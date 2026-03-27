---
name: nb-query
description: |
  NotebookLM 深度查询 Skill：超富集模式查询，自动存储中间产物，外部检索核查准确性，本地图片溯源。
  触发词：/nb-query、nb-query、智能笔记本查询、「从笔记本查询 XXX 并列出来源」、「查一下我的文章库里关于 XXX 的内容」
  适用场景：需要详尽资料 + 引用溯源 + 事实核查的查询任务；为写作收集带引用的素材。
---

# NotebookLM 深度查询（带引用溯源 + 核查 + 本地图片溯源）

对 NotebookLM Skill 的增强 Wrapper，采用**超富集模式**查询。

## 核心理念

1. **超富集查询**：不追求言简意赅，尽可能搜集资料，宁多勿少
2. **过程可追溯**：所有中间产物存储到工作目录，支持断点续查
3. **外部核查**：强制使用外部检索验证关键信息的准确性和时效性
4. **本地图片溯源**：不依赖 NotebookLM 的图片输出，从本地文章存档中提取正确的图片

## 工作目录结构

```
~/Downloads/nb-query-<主题关键词>-<日期>/
├── 00-metadata.md              # 任务元信息
├── 01-raw-response.json        # NotebookLM 原始 JSON 输出
├── 02-raw-answer.md            # 原始回答（带引用序号）
├── 02-raw-answer-with-images.md # 带图片的回答
├── 03-citation-map.json        # 序号 → 标题映射
├── 03-title-stats.json         # 文章统计
├── 03-citation-table.md        # 引用对照表（含链接）
├── 03.1-link-results.json      # 链接映射结果
├── 03.5-all-images.json        # 原始图片列表
├── 03.5-image-mapping.json     # 过滤后的图片映射
├── 04-fact-verification.md     # 外部检索核查结果
└── 05-final.md                 # 最终输出
```

## 执行流程

### 阶段 -1：同步知识库（BLOCKING）

每次查询前，先确保本地文章存档与 NotebookLM 同步：

```bash
/sync-notebooklm-kb
```

### 阶段 0：初始化与依赖检查

```bash
# 创建工作目录
WORK_DIR=~/Downloads/nb-query-<topic-in-english>-$(date +%Y%m%d)
mkdir -p "$WORK_DIR"

# 检查本地文章存档依赖
python scripts/check_articles_dir.py
```

命名规范：主题用英文/拼音，如 `nb-query-ai-tools-workflow-20260115`

写入 `00-metadata.md`：任务元信息（时间、查询主题、笔记本、状态）

### 阶段 1：准备阶段

```bash
# 确认笔记本上下文
notebooklm status

# 获取 source 列表（必须用 --json）
notebooklm source list --json > /tmp/nb_sources_raw.json

# 构建映射表
python scripts/build_source_mapping.py
```

### 阶段 2：超富集查询

**查询 prompt 模板**（强制详细 + 禁止图片输出）：

```
请针对以下问题，提供**尽可能详尽、全面**的回答：
{用户的原始问题}

要求：
1. 不要精简：宁可冗长也不要遗漏
2. 超富集搜集：所有相关内容都整合进来
3. 多角度覆盖：从不同维度汇总信息
4. 保留细节：具体数字、日期、案例都保留
5. 标注引用：每个信息点都标注 [1], [2] 等
6. 不做总结性压缩
7. 禁止输出图片链接
8. 标记配图位置：用 <!-- IMAGE_PLACEHOLDER: [引用号] --> 标记
```

```bash
notebooklm ask "..." --json > "$WORK_DIR/01-raw-response.json"
```

从 JSON 提取 answer 写入 `02-raw-answer.md`

### 阶段 3：生成引用对照表

```bash
WORK_DIR="$WORK_DIR" python scripts/generate_citation_table.py
```

### 阶段 3.1：添加外部链接

```bash
WORK_DIR="$WORK_DIR" python scripts/add_article_links.py
```

输出：`03-citation-table.md`（含链接）

### 阶段 3.5：本地图片溯源

```bash
# 提取图片
WORK_DIR="$WORK_DIR" python scripts/extract_images.py

# 匹配并插入图片
WORK_DIR="$WORK_DIR" python scripts/match_images.py
```

**题图识别**：脚本默认过滤 `position_in_article=0` 的图片。如需更精确识别，用 Claude Read 工具读取图片判断视觉特征。

### 阶段 4：外部检索核查（BLOCKING）

核查目标：
- **P0**: 软件/模型版本号（最易过时）
- **P1**: 产品功能描述
- **P2**: 具体数字
- **P3**: 日期和时间点

核查数量：至少 3-5 个 P0/P1 级别项目

写入 `04-fact-verification.md`：待核查项清单、核查结果、核查汇总、时效性评估

### 阶段 5：生成最终输出

整合到 `05-final.md`：回答 + 引用对照表 + 核查意见

### 阶段 5.5：素材过饱和输出

自动调用 `material-to-markdown` 生成素材文档。

### 阶段 6：打包输出（BLOCKING）

```bash
tar -czvf ~/outcome.tar.gz -C ~/Downloads \
    "nb-query-<topic>-<date>" \
    "material-<topic>-<date>"
```

## 存储执行规则

1. **即时写入**：每完成一个阶段，立即写入对应文件
2. **不可跳过**：即使结果简单，也必须创建对应文件
3. **外部核查必做**：阶段 4 不可跳过

## 与原生 NotebookLM Skill 的关系

| 场景 | 使用哪个 Skill |
|------|----------------|
| 简单查询，不需要来源追溯 | 原生 `notebooklm` |
| 需要详尽资料 + 核查 | 本 Skill `/nb-query` |
| 生成播客、视频等 artifact | 原生 `notebooklm` |
| 为写作收集带引用的素材 | 本 Skill `/nb-query` |

## 经验教训

### 1. Source Mapping 必须用 JSON 格式

文本表格格式存在严重解析问题（UUID 截断、中文标题跨行）。始终用 `--json`。

### 2. 工作目录命名避免中文

中文路径在某些工具链中可能出现编码问题，用英文/拼音。

### 3. 核查重点放在版本号和产品功能

AI 领域信息迭代极快，最容易出错的是模型版本号和产品功能描述。

### 4. NotebookLM 图片输出的致命缺陷

NotebookLM 输出的图片描述经常与实际内容不符（张冠李戴），因为 `references` 结构中没有图片来源元数据。解决：禁止输出图片，改从本地存档溯源。

### 5. 题图识别：读图判断优于硬编码

用 Claude 读图识别，而非硬编码"跳过前 N 行"。

### 6. 字符串多处替换必须逆序

```python
# ✅ 逆序替换，不影响前面位置
for i in range(len(matches) - 1, -1, -1):
    m = matches[i]
    text = text[:m.start()] + replacement + text[m.end():]
```

## 版本历史

| 版本 | 变更 |
|------|------|
| v1.5.0 | 本地图片溯源：禁止 NotebookLM 输出图片，改从本地存档提取 |
| v1.7.0 | 题图识别改为读图判断；添加依赖检查 |
| v1.11.0 | 图片匹配改为内容关键词策略 |
| v1.12.0 | 新增阶段 3.1，调用 article-linker 添加外部链接 |
| v2.0.0 | **重构**：脚本独立到 scripts/ 目录，SKILL.md 精简 |
