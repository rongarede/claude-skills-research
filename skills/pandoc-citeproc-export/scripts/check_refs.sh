#!/bin/bash
# ============================================================
# check_refs.sh: 校验 tex 引用键与 bib 条目的匹配关系
# ============================================================

set -e

# ==================== 默认配置 ====================
BIB_FILE="refs.bib"
TEX_FILES=""

# ==================== 参数解析 ====================
while [[ $# -gt 0 ]]; do
  case $1 in
    --bib) BIB_FILE="$2"; shift 2 ;;
    --tex) TEX_FILES="$2"; shift 2 ;;
    -h|--help)
      echo "用法: check_refs.sh [--bib FILE] [--tex 'file1.tex file2.tex ...']"
      echo "  若未指定 --tex，自动扫描当前目录下所有 .tex 文件"
      exit 0 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

# ==================== 依赖检查 ====================
if ! command -v python3 &> /dev/null; then
  echo "错误: 需要 python3"
  exit 1
fi

# ==================== 自动发现 tex 文件 ====================
if [ -z "$TEX_FILES" ]; then
  TEX_FILES=$(ls *.tex 2>/dev/null || true)
  if [ -z "$TEX_FILES" ]; then
    echo "错误: 当前目录下未找到 .tex 文件"
    exit 1
  fi
fi

# ==================== 主逻辑 ====================
python3 -c "
import re, sys

bib_file = '$BIB_FILE'
tex_files = '''$TEX_FILES'''.split()

# 提取 bib 条目键
bib_keys = set()
with open(bib_file) as f:
    for m in re.findall(r'@\w+\{(\w+)', f.read()):
        bib_keys.add(m.strip())

# 提取 tex 引用键
tex_keys = set()
for tf in tex_files:
    try:
        with open(tf) as f:
            for m in re.findall(r'\\\\cite\{([^}]+)\}', f.read()):
                for k in m.split(','):
                    tex_keys.add(k.strip())
    except FileNotFoundError:
        print(f'警告: {tf} 不存在，跳过')

# 输出结果
missing = sorted(tex_keys - bib_keys)
unused = sorted(bib_keys - tex_keys)

print(f'bib 条目数: {len(bib_keys)}')
print(f'tex 引用键数: {len(tex_keys)}')
print()

if missing:
    print(f'✗ tex 引用但 bib 缺失 ({len(missing)}):')
    for k in missing:
        print(f'  - {k}')
    sys.exit(1)
else:
    print('✓ 所有引用键在 bib 中均有定义')

print()
if unused:
    print(f'⚠ bib 存在但 tex 未引用 ({len(unused)}):')
    for k in unused:
        print(f'  - {k}')
else:
    print('✓ bib 中所有条目均被引用')
"
