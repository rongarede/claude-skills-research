#!/usr/bin/env python3
"""
阶段 1：构建 source ID → 文章标题的映射表
从 NotebookLM 的 JSON 输出构建映射
"""
import json
import sys

def main():
    input_file = sys.argv[1] if len(sys.argv) > 1 else '/tmp/nb_sources_raw.json'
    output_file = sys.argv[2] if len(sys.argv) > 2 else '/tmp/nb_source_mapping.json'

    with open(input_file, 'r') as f:
        data = json.load(f)

    mapping = {}
    for source in data.get('sources', []):
        sid = source.get('id', '')
        title = source.get('title', '').replace('.md', '')
        if sid and title:
            mapping[sid] = title

    with open(output_file, 'w') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)

    print(f"✓ 已缓存 {len(mapping)} 个来源映射 → {output_file}")

if __name__ == '__main__':
    main()
