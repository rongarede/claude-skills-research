---
name: sci-hub-download
description: 通过 DOI 下载论文 PDF，三路线组合（OA直链 → Sci-Hub镜像 → 出版商直连）。触发词：/sci-hub、下载论文、sci-hub下载、DOI下载
allowed-tools: [Bash, Read, Write]
---

# 论文 PDF 下载（三路线）

通过 DOI 自动尝试三条下载路线，成功率高于单一 Sci-Hub。

## 路线优先级

```
DOI 输入
  │
  ▼
路线1: 开放获取直链（OA，免费最快）
  ├─ MDPI (10.3390/*)        → mdpi.com PDF 直链
  ├─ IEEE Access (10.1109/ACCESS*) → IEEE stampPDF 直链
  ├─ PLoS (10.1371/*)        → plos.org 直链
  ├─ Frontiers (10.3389/*)   → frontiersin.org 直链
  └─ Unpaywall API 兜底      → 任意 OA 期刊
  │
  失败 ▼
路线2: Sci-Hub 镜像（覆盖 2022 年前论文）
  ├─ sci-hub.mksa.top → sci-hub.se → sci-hub.st → sci-hub.ren → sci-hub.ru
  │
  失败 ▼
路线3: 出版商直连（部分 IEEE/Springer/Elsevier OA）
  ├─ IEEE Xplore stampPDF 直链
  ├─ Springer link.springer.com PDF
  └─ ScienceDirect pdfft 直链
  │
  全部失败 → 报告失败并提示手动下载地址
```

## 使用场景

- 给定 DOI 下载单篇论文
- 批量下载多篇论文（DOI 列表文件）
- 指定输出目录
- 强制使用特定 Sci-Hub 镜像

## 快速开始

### 依赖安装
```bash
pip install requests beautifulsoup4
```

### CLI 用法
```bash
SCRIPTS=~/.claude/skills/sci-hub-download/scripts

# 下载单篇论文（自动三路线）
python3 $SCRIPTS/download.py "10.1109/TNNLS.2023.3310935"

# 指定输出目录
python3 $SCRIPTS/download.py "10.1109/TNNLS.2023.3310935" -o ~/Papers/

# 批量下载（DOI 列表文件，每行一个 DOI）
python3 $SCRIPTS/download.py -f dois.txt -o ~/Papers/

# 指定 Sci-Hub 镜像（路线2专用，路线1和3不受影响）
python3 $SCRIPTS/download.py "10.1109/xxx" --mirror sci-hub.st
```

## 参数说明

| 参数 | 说明 |
|------|------|
| `doi` | 论文 DOI（位置参数） |
| `-f FILE` | DOI 列表文件（每行一个，`#` 开头为注释） |
| `-o DIR` | 输出目录（默认当前目录） |
| `--mirror HOST` | 强制使用指定 Sci-Hub 镜像（路线2专用） |
| `--timeout N` | 请求超时秒数（默认 30） |

## 注意事项

- Sci-Hub 数据库自 2022 年冻结，2023 年后发表的论文优先依赖路线1（OA）
- 自动继承系统代理设置（http_proxy/https_proxy）
- 下载内容用魔数（`%PDF-`）校验，非 PDF 自动跳过并尝试下一路线
- 批量下载时每篇间隔 2 秒，避免被封
