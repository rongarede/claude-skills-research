#!/usr/bin/env python3
"""
从 Semantic Scholar raw JSON 生成统一格式的 Markdown 文件

用法:
  # 导出指定目录下所有 layer_*_raw.json → layer_*_results.md
  python export_md.py /path/to/results/

  # 导出指定文件
  python export_md.py layer_1_raw.json layer_2_raw.json

  # 自定义 layer 标题映射
  python export_md.py /path/to/results/ --titles '{"1":"综述","2":"信誉"}'
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# pylint: disable=wrong-import-position
from file_utils import find_json_files  # noqa: E402


# ── 默认 layer 标题 ───────────────────────────────────────

DEFAULT_TITLES = {
    "1": "车联网区块链共识综述",
    "2": "信誉/信任驱动共识",
    "3": "BFT/PBFT 共识改进",
    "4": "委托/委员会选举与分层架构",
    "5": "DAG 区块链共识",
    "6": "车联网边缘计算与区块链",
    "7": "安全与特定应用",
    "8": "HotStuff 协议家族",
    "9": "DAG-BFT 基础理论",
    "10": "攻击模型与密码学基础",
}


# ── JSON 解析 ─────────────────────────────────────────────

def parse_layer_num(path: Path) -> str | None:
    """从文件名提取 layer 编号"""
    m = re.search(r"layer_(\d+)_raw\.json", path.name)
    return m.group(1) if m else None


def load_json(path: Path) -> tuple[dict[str, list[dict]], dict[str, dict]]:
    """读取 raw JSON，返回 (queries, unique_papers)"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 统一为 {query: [papers]}
    if "results" in data:
        queries = {q: v["data"] for q, v in data["results"].items()}
    else:
        queries = {k: v for k, v in data.items() if isinstance(v, list)}

    # 去重
    papers = {}
    for papers_list in queries.values():
        for p in papers_list:
            pid = p.get("paperId")
            if pid and pid not in papers:
                papers[pid] = p

    return queries, papers


# ── 格式化工具 ────────────────────────────────────────────

def fmt_authors(authors: list[dict], limit: int = 3) -> str:
    """格式化作者列表，超过 limit 时截断并标注总数"""
    if not authors:
        return "N/A"
    names = [a.get("name", "") for a in authors[:limit]]
    s = ", ".join(names)
    if len(authors) > limit:
        s += f" 等 ({len(authors)} 人)"
    return s


def fmt_venue(paper: dict) -> str:
    """提取期刊/会议名称，优先用 venue 字段"""
    venue = paper.get("venue") or ""
    if not venue:
        journal = paper.get("journal")
        if journal and isinstance(journal, dict):
            venue = journal.get("name", "")
    return venue or "N/A"


def fmt_doi(paper: dict) -> str:
    """格式化 DOI 或 ArXiv ID 为 Markdown 链接"""
    ext = paper.get("externalIds") or {}
    if doi := ext.get("DOI", ""):
        return f"[{doi}](https://doi.org/{doi})"
    if arxiv := ext.get("ArXiv", ""):
        return f"[arXiv:{arxiv}](https://arxiv.org/abs/{arxiv})"
    return "N/A"


def paper_link(paper: dict) -> str:
    """生成论文在 Semantic Scholar 上的链接"""
    if url := paper.get("url", ""):
        return url
    pid = paper.get("paperId", "")
    return f"https://www.semanticscholar.org/paper/{pid}" if pid else ""


# ── Markdown 生成 ─────────────────────────────────────────

def generate_md(layer_num: str, title: str,
                queries: dict[str, list[dict]],
                papers: dict[str, dict]) -> str:
    """生成统一格式的 Markdown"""
    keywords = ", ".join(queries.keys())
    sorted_papers = sorted(
        papers.values(),
        key=lambda x: x.get("citationCount", 0),
        reverse=True,
    )

    lines = [
        f"# Semantic Scholar 搜索结果 - Layer {layer_num}: {title}",
        "",
        f"**搜索主题**: {keywords}",
        "",
        f"**总论文数**: {len(sorted_papers)}",
        "",
        "",
        "## 论文列表",
        "",
        "| # | 标题 | 作者 | 年份 | 引用 | 期刊/会议 |",
        "|---|------|------|------|------|----------|",
    ]

    for i, p in enumerate(sorted_papers, 1):
        t = (p.get("title") or "N/A")[:80]
        if len(p.get("title", "")) > 80:
            t += "..."
        lines.append(
            f"| {i} | {t} | {fmt_authors(p.get('authors', []))} "
            f"| {p.get('year', 'N/A')} | {p.get('citationCount', 0)} "
            f"| {fmt_venue(p)} |"
        )

    lines.extend(["", "## 详细内容", ""])

    for i, p in enumerate(sorted_papers, 1):
        link = paper_link(p)
        lines.append(f"### {i}. {p.get('title', 'N/A')}")
        lines.append("")
        if link:
            lines.append(f"- **链接**: {link}")
        lines.extend([
            f"- **期刊/会议**: {fmt_venue(p)}",
            f"- **年份**: {p.get('year', 'N/A')}",
            f"- **引用数**: {p.get('citationCount', 0)}",
            f"- **DOI**: {fmt_doi(p)}",
            "",
        ])
        abstract = p.get("abstract")
        lines.append(f"**摘要**:\n\n{abstract}" if abstract else "**摘要**: 暂无")
        lines.extend(["", ""])

    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────

def main():
    """CLI 入口：解析参数并执行 Markdown 导出"""
    parser = argparse.ArgumentParser(
        description="从 Semantic Scholar raw JSON 生成统一格式的 Markdown"
    )
    parser.add_argument(
        "paths", nargs="+",
        help="目录路径（自动扫描 layer_*_raw.json）或具体 JSON 文件路径"
    )
    parser.add_argument(
        "--titles", type=str, default=None,
        help='自定义 layer 标题映射 JSON，如 \'{"1":"综述","2":"信誉"}\''
    )
    args = parser.parse_args()

    titles = dict(DEFAULT_TITLES)
    if args.titles:
        titles.update(json.loads(args.titles))

    # 收集文件
    files = find_json_files(args.paths)

    if not files:
        print("未找到任何 JSON 文件", file=sys.stderr)
        return

    for f in files:
        layer_num = parse_layer_num(f)
        if not layer_num:
            # 非 layer 格式文件，用文件名作标题
            layer_num = f.stem.replace("_raw", "")
        title = titles.get(layer_num, f"Layer {layer_num}")

        queries, papers = load_json(f)
        md = generate_md(layer_num, title, queries, papers)

        out_path = f.parent / f.name.replace("_raw.json", "_results.md")
        with open(out_path, "w", encoding="utf-8") as fp:
            fp.write(md)

        has_abs = sum(1 for p in papers.values() if p.get("abstract"))
        print(f"{out_path.name}: {len(papers)} 篇论文，{has_abs} 篇有摘要")

    print("\n完成！")


if __name__ == "__main__":
    main()
