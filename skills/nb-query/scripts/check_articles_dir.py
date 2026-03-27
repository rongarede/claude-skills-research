#!/usr/bin/env python3
"""
阶段 0：检查本地文章存档依赖
支持多环境路径自动检测（macOS Dropbox / VPS /tmp）
"""
import os
import json
import sys
from pathlib import Path

def main():
    # 多环境路径检测（按优先级）
    possible_paths = [
        Path.home() / 'Dropbox/cn_articles_published/all',  # macOS
        Path('/tmp/cn_articles_published/all'),              # VPS remote 模式
    ]

    articles_dir = None
    for p in possible_paths:
        if p.exists():
            articles_dir = p
            break

    # 检查 1：目录是否存在
    if not articles_dir:
        print("❌ 本地文章存档不存在")
        print(f"已检查路径: {[str(p) for p in possible_paths]}")
        print("请先运行 /sync-notebooklm-kb 同步文章")
        sys.exit(1)

    print(f"✓ 使用文章存档: {articles_dir}")

    # 检查 2：文件数量是否合理
    md_files = list(articles_dir.glob('*.md'))
    if len(md_files) < 10:
        print(f"⚠️ 本地文章数量偏少（{len(md_files)} 篇），可能需要同步")

    # 检查 3：与 NotebookLM source 数量对比（如果有缓存）
    nb_sources_file = Path('/tmp/nb_sources_raw.json')
    if nb_sources_file.exists():
        with open(nb_sources_file, 'r') as f:
            nb_sources = json.load(f).get('sources', [])

        local_count = len(md_files)
        nb_count = len(nb_sources)
        diff = abs(local_count - nb_count)

        if diff > 5:
            print(f"⚠️ 本地文章（{local_count}）与 NotebookLM（{nb_count}）数量差异较大")
            print("建议运行 /sync-notebooklm-kb 同步")
        else:
            print(f"✓ 存档检查通过：本地 {local_count} 篇，NotebookLM {nb_count} 篇")
    else:
        print(f"✓ 本地文章 {len(md_files)} 篇（NotebookLM 缓存不存在，跳过对比）")

    # 保存检测到的路径供后续阶段使用
    with open('/tmp/nb_articles_dir.txt', 'w') as f:
        f.write(str(articles_dir))

    print(f"✓ 路径已保存到 /tmp/nb_articles_dir.txt")

if __name__ == '__main__':
    main()
