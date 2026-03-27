#!/usr/bin/env python3
"""
批量补全 Semantic Scholar 搜索结果中缺失的摘要

用法:
  # 补全指定目录下所有 layer_*_raw.json
  python batch_abstract.py /path/to/results/

  # 补全指定文件
  python batch_abstract.py layer_1_raw.json layer_2_raw.json

  # 仅检查缺失情况，不实际请求
  python batch_abstract.py /path/to/results/ --dry-run
"""

import argparse
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# pylint: disable=wrong-import-position
from s2_client import S2Client  # noqa: E402
from file_utils import find_json_files  # noqa: E402


def extract_papers(data: dict) -> list[dict]:
    """从 raw JSON 中提取所有论文对象的引用（原地修改用）"""
    papers = []
    # 格式 A: {"mode": ..., "results": {"query": {"total": N, "data": [...]}}}
    if "results" in data:
        for query_result in data["results"].values():
            papers.extend(query_result.get("data", []))
    # 格式 B: {"query": [papers]}
    else:
        for val in data.values():
            if isinstance(val, list):
                papers.extend(val)
    return papers


def collect_missing(papers: list[dict]) -> list[str]:
    """收集缺少 abstract 的 paperId（去重）"""
    seen: set[str] = set()
    missing: list[str] = []
    for p in papers:
        pid = p.get("paperId")
        if not pid or pid in seen:
            continue
        seen.add(pid)
        if p.get("abstract") is None:
            missing.append(pid)
    return missing


# ── 异步主逻辑 ────────────────────────────────────────────


def _scan_files(files):
    """扫描 JSON 文件，返回 (file_data, unique_missing_ids)"""
    file_data = {}  # {path: (raw_data, papers)}
    all_missing = []
    for f in files:
        with open(f, "r", encoding="utf-8") as fp:
            raw = json.load(fp)
        papers = extract_papers(raw)
        missing = collect_missing(papers)
        file_data[f] = (raw, papers)
        all_missing.extend(missing)
        print(f"{f.name}: {len(papers)} 篇论文，{len(missing)} 篇缺少摘要")
    unique_missing = list(dict.fromkeys(all_missing))
    print(f"\n共需补全 {len(unique_missing)} 篇（去重后）")
    return file_data, unique_missing


def _write_back(file_data, abstracts):
    """将获取到的摘要写回原 JSON 文件"""
    print("\n正在更新 JSON 文件...")
    for f, (raw, papers) in file_data.items():
        updated = 0
        for p in papers:
            pid = p.get("paperId")
            has_abstract = "abstract" in p and p["abstract"] is not None
            if pid in abstracts and not has_abstract:
                p["abstract"] = abstracts[pid]
                updated += 1
        with open(f, "w", encoding="utf-8") as fp:
            json.dump(raw, fp, ensure_ascii=False, indent=2)
        print(f"  {f.name}: 更新了 {updated} 篇")


async def run(args):
    """扫描 JSON 文件，批量获取并回填缺失的摘要"""
    files = find_json_files(args.paths)
    if not files:
        print("未找到任何 JSON 文件", file=sys.stderr)
        return

    file_data, unique_missing = _scan_files(files)

    if args.dry_run:
        print("(dry-run 模式，不实际请求)")
        return
    if not unique_missing:
        print("所有论文已有摘要，无需请求")
        return

    # 通过 S2Client 批量获取摘要
    client = S2Client(api_key=args.api_key, cache=False)
    try:
        print("\n正在从 Semantic Scholar API 获取摘要...")
        results = await client.batch_papers(unique_missing, fields="abstract")
    finally:
        await client.close()

    abstracts = {r["paperId"]: r.get("abstract")
                 for r in results if r and "paperId" in r}
    fetched = sum(1 for v in abstracts.values() if v is not None)
    print(f"成功获取 {fetched} 篇有效摘要，"
          f"{len(abstracts) - fetched} 篇确认无摘要")

    _write_back(file_data, abstracts)

    print("\n完成！")


# ── CLI ───────────────────────────────────────────────────

def main():
    """CLI 入口：解析参数并执行摘要补全"""
    parser = argparse.ArgumentParser(
        description="批量补全 Semantic Scholar 搜索结果中缺失的摘要"
    )
    parser.add_argument(
        "paths", nargs="+",
        help="目录路径（自动扫描 layer_*_raw.json）或具体 JSON 文件路径"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="仅检查缺失情况，不实际请求 API"
    )
    parser.add_argument(
        "--api-key", help="S2 API Key（也可设 S2_API_KEY 环境变量）"
    )
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
