---
name: paper-mapping
description: "论文段落级仿写映射工具：在同领域同思想框架前提下，建立论文段落间的结构、逻辑、方法映射关系。触发词：/mapping、论文映射、段落映射"
---

# 论文映射工具

在同领域同思想框架前提下，建立论文段落级仿写映射关系。

## 触发方式

- `/mapping <目标文件>`
- 「帮我做论文映射」
- 「建立段落映射关系」

## 工作流程

1. 接收目标文件路径
2. **本地分析**：读取目标文档，逐段落提取核心概念，聚类为 3-5 个主题关键词组
3. **nb-query 轻量检索**：对每个主题 query 调用 nb-query 从 NotebookLM 论文库检索候选段落
4. **源段落存档**：将 nb-query 返回的目标论文原文段落保存到 `source_paragraphs/` 目录
5. **合并去重**：按「论文标题 + 章节位置」去重，保留来源主题标签
6. 按四大维度判断映射关系
7. 输出结果到 `<目标文件>_mapping.md`

> **Fallback**: 若 NotebookLM 服务不可用，回退到扫描本地 `mdfile/` 目录下的 Markdown 文件

## 本地分析阶段

读取目标文档后，执行以下操作：

1. 逐段落提取核心概念（方法名、机制名、数学符号、关键术语）
2. 将概念聚类为 3-5 个主题关键词组
3. 每组构造一个面向 NotebookLM 的检索 query

**示例**（以 LightDAG 共识协议为例）：

```
T1: "DAG-based BFT consensus protocol leader election"
T2: "reputation scoring mechanism Byzantine fault tolerance"
T3: "RSU delegation vehicular network consensus"
T4: "latency optimization partial synchrony consensus"
T5: "experimental evaluation throughput latency BFT"
```

## nb-query 轻量检索模式

在 mapping 内部调用 nb-query 时，只执行核心检索子集：

| nb-query 阶段 | 执行? | 说明 |
|---|---|---|
| 阶段 -1: 同步知识库 | 首次一次 | 确保论文库最新，多次查询不重复同步 |
| 阶段 0: 初始化 | 执行 | 创建临时工作目录 `mapping-query-<日期>/` |
| 阶段 1: 准备 | 执行 | 获取 source 列表（`--json`），构建映射表 |
| 阶段 2: 超富集查询 | 执行 | 使用下方映射专用 prompt 模板 |
| 阶段 3: 引用对照表 | 执行 | 生成引用序号 → 论文标题映射 |
| 阶段 3.1+: 后续阶段 | 全部跳过 | 不需要外部链接、图片溯源、外部核查、打包 |

### 映射专用 prompt 模板

```
在论文库中检索与以下主题相关的具体段落和机制描述：{主题关键词}

要求：
1. 列出每个相关段落的来源论文、章节位置、核心概念
2. 描述该段落的具体方法/机制/实验设计
3. 标注该段落所属的研究范式（BFT增强/新协议设计/安全模型/性能优化）
4. 如有数学定义或公式，简述其物理含义
5. 【必须】逐字引用每个相关段落的原文（3-8句），用引用块标记
```

### 结果合并去重

- 多个主题 query 的检索结果可能重叠
- 按「论文标题 + 章节位置」去重
- 保留每条结果的来源主题标签，用于后续映射类型判断

## 源段落存档（步骤 4）

nb-query 返回结果后，**必须**将目标论文的原文段落保存到本地，供后续编写阶段参考。

### 目录结构

```
mapping/source_paragraphs/
├── <映射ID>_<论文别名>_<章节>.md    # 每条映射一个文件
├── M01_TECChain_§3.1.md
├── M02_EBRC_§2.1.md
├── ...
└── index.md                         # 索引文件
```

### 单文件格式

```markdown
# M01: TECChain §3.1 — edge–edge collaboration management framework

## 原文（逐字提取，保持原始语言）

> In the classic edge computing model, the computing architecture is organized
> as a Cloud-Edge-End hierarchy...
> [3-8句原文]

## 来源信息

- 论文: A blockchain-based scheme for edge–edge collaboration management in TSN
- 章节: §3.1
- 检索主题: T1 (IoV RSU delegation consensus architecture)
- 映射类型: Contextual
- 仿写层: 问题表述
```

### 索引文件 `index.md`

```markdown
# 源段落索引

| 映射ID | 论文 | 章节 | 文件 |
|--------|------|------|------|
| M01 | TECChain | §3.1 | M01_TECChain_§3.1.md |
| M02 | EBRC | §2.1 | M02_EBRC_§2.1.md |
```

### 存档规则

1. nb-query 返回的原文段落**必须逐字保存**，不得改写或翻译
2. 若 nb-query 未返回原文（仅返回摘要），则从本地 `mdfile/` 中定位并提取对应段落
3. 每条映射对应的原文控制在 3-8 句
4. 目录不存在时自动创建

## 前置硬性约束

在任何映射判断之前，必须先满足以下前置条件：

### 1. 领域一致（Same Domain）
- 我的论文与候选论文必须研究同一类问题域
- 例如：BFT 共识 / 区块链协议 / 网络安全 / IoV / 分布式系统
- 若仅场景相似但研究对象不同（如 PoS vs BFT），禁止映射

### 2. 思想框架一致（Same Paradigm）
- 双方必须采用相同的问题建模范式
- 例如：在既有共识协议（HotStuff / PBFT）框架内进行增强
- 若对方论文属于"完全重设计新协议 / 新安全模型"，禁止映射

**只要上述任一条件不满足，直接判定：不建立映射**

## 四大映射判断维度

### 1. 概念指纹匹配（Concept Fingerprint Matching）

判断标准：
- 不看名称是否一致，而看**物理含义或数学内核是否等价或高度相似**

判断流程：
- 从我的段落中抽取关键概念（如：EDR、信誉衰减、Leader 惩罚）
- 在候选论文中寻找：
  - 数学形式等价（如乘法惩罚 ≈ 指数衰减）
  - 逻辑功能等价（如信誉抑制 ≈ 长期恶意节点隔离）

### 2. 场景特征可迁移性（Scenario Transferability）

判断标准：
- 不要求应用场景名称相同
- 但要求**底层系统约束高度同构**

重点比较：
- 延迟 / 实时性要求
- 网络同步假设
- 节点资源受限程度
- 对鲁棒性和可预测性的要求

### 3. 功能模块互补性（Functional Modularity）

判断标准：
- 我的论文中是否存在某一"机制短板"
- 候选论文中是否存在**可独立抽取的功能模块**用于补全该短板

典型情形：
- 原始 HotStuff 缺乏动态节点管理 → 借鉴动态加入/退出模块
- 原始 BFT 选主机制过于静态 → 借鉴信誉驱动选主思想

### 4. 实验范式复刻价值（Experimental Paradigm Matching）

判断标准：
- 我的论文是否需要证明某一核心卖点
- 候选论文是否提供了成熟的实验范式来证明同类卖点

重点关注：
- 自变量设计（如恶意节点比例、批大小、节点规模）
- 性能指标选择（TPS、Latency、Leader 命中率）
- 对照组设置方式

## 快速决策优先级

按以下顺序判断，一旦命中即可映射：

1. **名称直接匹配（Nominal Match）**
   - 如 VRF ↔ VRF，Threshold Signature ↔ Threshold Signature

2. **内核原理匹配（Intrinsic Match）**
   - 如 EDR ↔ Multiplicative Penalty / Reputation Decay

3. **短板补全匹配（Complementary Match）**
   - 如 HotStuff 静态假设 ↔ 动态成员管理机制

4. **环境约束匹配（Contextual Match）**
   - 如 IoV ↔ TSN / IoT 在实时性与资源约束上的同构性

## 禁止的映射行为

- 禁止仅因"文字相似"而建立映射
- 禁止跨思想框架（如 BFT ↔ PoS）映射
- 禁止将整篇论文作为映射对象，映射必须是**段落级或模块级**
- 禁止为了凑 Related Work 而强行映射

## 输出文件规范

### 文件名
`<目标文件>_mapping.md`

### 格式要求

**只保留一个扁平映射表，禁止多视图重复。**

文件结构：
1. 标题行（含目标文档路径、章节、日期）
2. 段落索引表（段落编号 | 行号 | 一句话概述，不贴原文）
3. 映射主表（每条映射一行）

### 映射主表字段

| 字段 | 说明 |
|------|------|
| ID | M01, M02... |
| 源段落 | P1, P2-1, P2-2 等 |
| 类型 | Intrinsic / Contextual / Complementary / Nominal |
| 目标论文 | 原始 PDF 文件名或别名（文件头定义别名表） |
| 目标位置 | §原文章节标题: 关键术语（用于 NotebookLM 检索） |
| 理由 | 一句话，≤30字 |
| 仿写层 | 问题表述 / 方法思想 / 机制设计 / 实验范式 |

### 禁止内容

- 禁止引用原文段落全文（只写编号+概述）
- 禁止输出「仿写建议」「引用建议」「优先级排序」「总结」等写作指导
- 禁止同一映射数据出现两种组织视图（按段落 vs 按维度）
- 单章节映射文件不超过 80 行

### 输出约束

- 映射结果严禁在终端直接展示，必须以文件形式保存
- 若文件已存在，追加或更新对应条目，严禁覆盖
- 禁止生成任何论文正文或改写文本
