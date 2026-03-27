#!/usr/bin/env python3
"""
阶段 3.1：为引用添加外部链接
从 platform_info.json 查找文章的发布链接
"""
import json
import os
import re
import sys
from pathlib import Path

# 平台优先级
PRIORITY = ['微信', '知乎', '少数派', '头条', '百家号', '小报童', 'zsxq', 'substack', 'medium_eng']
SKIP_FIELDS = {'标题', 'monetize', 'id', 'date', 'tags', ''}

def normalize(t):
    """标准化标题，用于模糊匹配"""
    t = re.sub(r'[《》「」"""]', '', t)
    t = re.sub(r'\s+', ' ', t).strip()
    t = t.replace('：', ':').replace('，', ',')
    return t

def main():
    work_dir = os.environ.get('WORK_DIR') or sys.argv[1] if len(sys.argv) > 1 else '.'

    # 加载阶段 3 的数据
    with open(f'{work_dir}/03-citation-map.json', 'r') as f:
        citation_table = json.load(f)
        citation_table = {int(k): v for k, v in citation_table.items()}

    with open(f'{work_dir}/03-title-stats.json', 'r') as f:
        stats = json.load(f)
        title_to_citations = stats['title_to_citations']
        source_counts = stats['source_counts']
        sorted_titles = stats['sorted_titles']

    # 加载 platform_info.json
    platform_file = Path.home() / ".local/share/platform-sheets/platform_info.json"
    link_results = {}

    if not platform_file.exists():
        print("⚠️ platform_info.json 不存在，跳过链接映射")
        print("请运行 /sync-platform-sheets 同步数据")
        for num in citation_table:
            link_results[num] = (None, None, 'none')
    else:
        with open(platform_file, 'r', encoding='utf-8') as f:
            platform_data = json.load(f)

        # 构建标题 → URL 映射
        title_to_url = {}
        for item in platform_data:
            title = item.get('标题', '').strip()
            if not title:
                continue
            for p in PRIORITY:
                u = item.get(p, '').strip()
                if u:
                    title_to_url[title] = (u, p)
                    break
            # 回退：任意非空链接
            if title not in title_to_url:
                for k, v in item.items():
                    if k not in SKIP_FIELDS and v and str(v).startswith('http'):
                        title_to_url[title] = (v.strip(), k)
                        break

        normalized_map = {normalize(t): t for t in title_to_url.keys()}

        # 解析每个标题
        for num, query_title in citation_table.items():
            # 精确匹配
            if query_title in title_to_url:
                url, platform = title_to_url[query_title]
                link_results[num] = (url, platform, 'exact')
                continue
            # 标准化匹配
            normalized_query = normalize(query_title)
            if normalized_query in normalized_map:
                original = normalized_map[normalized_query]
                url, platform = title_to_url[original]
                link_results[num] = (url, platform, 'normalized')
                continue
            # 包含匹配
            matched = False
            for t, (u, p) in title_to_url.items():
                if query_title in t or t in query_title:
                    link_results[num] = (u, p, 'fuzzy')
                    matched = True
                    break
            if not matched:
                link_results[num] = (None, None, 'none')

    # 生成带链接的引用对照表
    with open(f'{work_dir}/03-citation-table.md', 'w') as f:
        f.write("# 引用对照表\n\n")
        f.write(f"共 {len(citation_table)} 个序号，来自 {len(title_to_citations)} 篇文章\n\n")

        # 统计匹配情况
        matched = sum(1 for r in link_results.values() if r[0])
        f.write(f"**链接映射**：匹配 {matched}/{len(citation_table)} 条")
        if len(citation_table) > 0:
            f.write(f"（{matched/len(citation_table)*100:.1f}%）")
        f.write("\n\n")

        # 表头
        f.write("| 来源文章 | 对应序号 | 引用次数 | 平台 | 链接 |\n")
        f.write("|----------|----------|:--------:|:----:|------|\n")

        for title in sorted_titles:
            citations = title_to_citations[title]
            count = source_counts.get(title, 0)

            # 序号字符串
            if len(citations) <= 10:
                citation_str = ', '.join(f'[{c}]' for c in citations)
            else:
                first_5 = ', '.join(f'[{c}]' for c in citations[:5])
                last_5 = ', '.join(f'[{c}]' for c in citations[-5:])
                citation_str = f'{first_5} ... {last_5}'

            # 获取链接
            first_num = citations[0]
            if first_num in link_results and link_results[first_num][0]:
                url, platform, _ = link_results[first_num]
                link_cell = f'[查看]({url})'
                platform_cell = platform
            else:
                link_cell = '-'
                platform_cell = '-'

            f.write(f"| {title} | {citation_str} | {count} | {platform_cell} | {link_cell} |\n")

        # 未匹配列表
        unmatched = [(num, citation_table[num]) for num, r in link_results.items() if not r[0]]
        if unmatched:
            f.write(f"\n## 未匹配的引用（{len(unmatched)} 条）\n\n")
            for num, title in sorted(unmatched):
                f.write(f"- [{num}] {title}\n")

    # 保存链接映射结果
    with open(f'{work_dir}/03.1-link-results.json', 'w') as f:
        serializable = {str(k): list(v) for k, v in link_results.items()}
        json.dump(serializable, f, ensure_ascii=False, indent=2)

    print(f"✓ 引用对照表已写入 {work_dir}/03-citation-table.md")
    print(f"  链接映射：{matched}/{len(citation_table)} 条匹配")

if __name__ == '__main__':
    main()
