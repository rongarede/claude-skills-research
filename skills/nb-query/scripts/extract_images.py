#!/usr/bin/env python3
"""
阶段 3.5：从本地文章存档提取图片
扫描引用最多的文章，提取所有图片链接
"""
import json
import os
import re
import sys
from pathlib import Path

def main():
    work_dir = os.environ.get('WORK_DIR') or sys.argv[1] if len(sys.argv) > 1 else '.'

    # 读取存档路径
    articles_dir_file = Path('/tmp/nb_articles_dir.txt')
    if articles_dir_file.exists():
        articles_dir = Path(articles_dir_file.read_text().strip())
    else:
        # 回退到默认路径
        articles_dir = Path.home() / 'Dropbox/cn_articles_published/all'

    if not articles_dir.exists():
        print(f"❌ 文章存档目录不存在: {articles_dir}")
        print("图片溯源功能降级为纯文本输出")
        sys.exit(0)

    # 加载映射表
    with open('/tmp/nb_source_mapping.json', 'r') as f:
        source_map = json.load(f)

    with open(f'{work_dir}/01-raw-response.json', 'r') as f:
        response = json.load(f)

    refs = response.get('references', [])

    # 统计各文章被引用次数
    source_counts = {}
    for ref in refs:
        sid = ref.get('source_id', '')
        title = source_map.get(sid, '未知来源')
        source_counts[title] = source_counts.get(title, 0) + 1

    # 取引用最多的前 10 篇
    top_articles = sorted(source_counts.items(), key=lambda x: -x[1])[:10]

    # 图片溯源结果
    all_images = []

    for title, count in top_articles:
        article_path = articles_dir / f"{title}.md"
        if not article_path.exists():
            continue

        with open(article_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 提取所有图片链接及其位置
        img_pattern = r'([\s\S]{0,100})!\[([^\]]*)\]\((https://[^)]+r2\.dev[^)]+)\)([\s\S]{0,100})'
        for i, match in enumerate(re.finditer(img_pattern, content)):
            before, alt, url, after = match.groups()
            context = (before.strip() + ' ' + after.strip())[:80]
            all_images.append({
                'source_article': title,
                'image_url': url,
                'context': context,
                'alt': alt,
                'position_in_article': i,  # 0 = 第一张图
                'char_position': match.start()
            })

    # 写入原始图片列表
    with open(f'{work_dir}/03.5-all-images.json', 'w') as f:
        json.dump(all_images, f, ensure_ascii=False, indent=2)

    print(f"✓ 共提取 {len(all_images)} 张图片，待题图识别过滤")
    print(f"  来自 {len([a for a, _ in top_articles if (articles_dir / f'{a}.md').exists()])} 篇文章")
    print("→ 下一步：用 Claude Read 工具识别题图，或直接过滤 position_in_article=0 的图片")

if __name__ == '__main__':
    main()
