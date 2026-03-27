#!/usr/bin/env python3
"""
阶段 3.5 续：图片匹配与插入
根据段落内容关键词匹配图片，逆序替换 placeholder
"""
import json
import os
import re
import sys
from pathlib import Path

# 关键词 → 文章映射表（按主题分类）
# 注意：这是示例映射，请根据你自己的文章库内容自定义
# 格式：r"关键词1|关键词2|关键词3": "对应的文章标题"
KEYWORD_TO_ARTICLE = {
    # 示例：教学相关
    r"课堂|教学|学生|教育": "示例：教学方法探讨",
    # 示例：AI 工具
    r"AI|人工智能|机器学习": "示例：AI 工具使用指南",
    # 示例：编程技术
    r"编程|代码|开发|Python": "示例：编程技术入门",
    # 添加你自己的关键词 → 文章映射...
    # r"你的关键词模式": "你的文章标题",
}

def find_article_for_paragraph(paragraph_text, keyword_map):
    """根据段落内容的关键词确定来源文章"""
    for pattern, article in keyword_map.items():
        if re.search(pattern, paragraph_text, re.IGNORECASE):
            return article
    return None

def select_image_for_placeholder(placeholder_match, answer_text, images_by_article, used_urls):
    """为 placeholder 选择合适的图片"""
    # 提取 placeholder 前后 500 字符作为上下文
    start = max(0, placeholder_match.start() - 500)
    end = min(len(answer_text), placeholder_match.end() + 200)
    context = answer_text[start:end]

    # 根据上下文关键词确定来源文章
    target_article = find_article_for_paragraph(context, KEYWORD_TO_ARTICLE)

    if target_article and target_article in images_by_article:
        for img in images_by_article[target_article]:
            if img['image_url'] not in used_urls:
                used_urls.add(img['image_url'])
                return img

    return None

def main():
    work_dir = os.environ.get('WORK_DIR') or sys.argv[1] if len(sys.argv) > 1 else '.'

    # 加载图片列表
    images_file = Path(f'{work_dir}/03.5-all-images.json')
    if not images_file.exists():
        print("⚠️ 图片列表不存在，跳过图片匹配")
        sys.exit(0)

    with open(images_file, 'r') as f:
        all_images = json.load(f)

    # 过滤题图（position_in_article = 0 的图片）
    # 注意：更精确的题图识别应该用 Claude 读图判断
    filtered_images = [img for img in all_images if img.get('position_in_article', 0) > 0]

    print(f"过滤题图后，剩余 {len(filtered_images)} 张可用配图")

    # 加载回答
    with open(f'{work_dir}/02-raw-answer.md', 'r') as f:
        answer = f.read()

    # 查找所有 placeholder
    placeholders = list(re.finditer(r'<!-- IMAGE_PLACEHOLDER: \[[\d,\s]+\] -->', answer))

    if not placeholders:
        print("未找到 IMAGE_PLACEHOLDER，跳过图片插入")
        # 保存过滤后的图片列表
        with open(f'{work_dir}/03.5-image-mapping.json', 'w') as f:
            json.dump(filtered_images, f, ensure_ascii=False, indent=2)
        sys.exit(0)

    # 按文章组织图片
    images_by_article = {}
    for img in filtered_images:
        article = img['source_article']
        if article not in images_by_article:
            images_by_article[article] = []
        images_by_article[article].append(img)

    # 为每个 placeholder 选择图片
    used_urls = set()
    selected = []
    for ph in placeholders:
        img = select_image_for_placeholder(ph, answer, images_by_article, used_urls)
        if img:
            selected.append({'placeholder': ph, 'image': img})

    # 逆序替换
    for i in range(len(selected) - 1, -1, -1):
        ph_match = selected[i]['placeholder']
        img = selected[i]['image']
        replacement = f'''

<!-- 图片来源：《{img['source_article']}》 -->
![{img.get('alt', '配图')}]({img['image_url']})

'''
        answer = answer[:ph_match.start()] + replacement + answer[ph_match.end():]

    # 保存带图片的回答
    with open(f'{work_dir}/02-raw-answer-with-images.md', 'w') as f:
        f.write(answer)

    # 保存图片映射
    with open(f'{work_dir}/03.5-image-mapping.json', 'w') as f:
        json.dump(filtered_images, f, ensure_ascii=False, indent=2)

    print(f"✓ 已插入 {len(selected)} 张图片")
    print(f"  输出文件: {work_dir}/02-raw-answer-with-images.md")

if __name__ == '__main__':
    main()
