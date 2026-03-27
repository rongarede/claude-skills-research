#!/usr/bin/env python3
"""
阶段 3：生成引用对照表
从 NotebookLM 响应中提取引用信息，构建序号 → 文章标题的映射
"""
import json
import os
import sys

def main():
    work_dir = os.environ.get('WORK_DIR') or sys.argv[1] if len(sys.argv) > 1 else '.'

    # 加载映射表
    with open('/tmp/nb_source_mapping.json', 'r') as f:
        source_map = json.load(f)

    # 加载响应
    with open(f'{work_dir}/01-raw-response.json', 'r') as f:
        response = json.load(f)

    refs = response.get('references', [])

    # 步骤 1: 构建序号 → 文章标题的映射（去重）
    citation_table = {}  # {序号: 文章标题}
    for ref in refs:
        cnum = ref.get('citation_number')
        sid = ref.get('source_id', '')
        title = source_map.get(sid, '未知来源')
        if cnum is not None and cnum not in citation_table:
            citation_table[cnum] = title

    # 步骤 2: 反转映射，按文章分组序号
    title_to_citations = {}  # {文章标题: [序号列表]}
    for cnum, title in citation_table.items():
        if title not in title_to_citations:
            title_to_citations[title] = []
        title_to_citations[title].append(cnum)

    # 对每个文章的序号列表排序
    for title in title_to_citations:
        title_to_citations[title].sort()

    # 步骤 3: 统计各文章被引用次数（用于排序）
    source_counts = {}
    for ref in refs:
        sid = ref.get('source_id', '')
        title = source_map.get(sid, '未知来源')
        source_counts[title] = source_counts.get(title, 0) + 1

    # 按引用次数排序
    sorted_titles = sorted(title_to_citations.keys(), key=lambda t: -source_counts.get(t, 0))

    # 保存 citation_table 供阶段 3.1 使用
    with open(f'{work_dir}/03-citation-map.json', 'w') as f:
        json.dump(citation_table, f, ensure_ascii=False, indent=2)

    # 保存 title_to_citations 和 source_counts 供阶段 3.1 使用
    with open(f'{work_dir}/03-title-stats.json', 'w') as f:
        json.dump({
            'title_to_citations': title_to_citations,
            'source_counts': source_counts,
            'sorted_titles': sorted_titles
        }, f, ensure_ascii=False, indent=2)

    print(f"✓ 引用映射已保存，共 {len(citation_table)} 个序号，来自 {len(title_to_citations)} 篇文章")
    print("→ 继续执行阶段 3.1：调用 add_article_links.py 添加外部链接")

if __name__ == '__main__':
    main()
