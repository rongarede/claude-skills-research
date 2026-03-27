#!/bin/bash
# ============================================================
# pandoc-citeproc-export: LaTeX → Word 带引用格式导出
# ============================================================

set -e

# ==================== 默认配置 ====================
TEX_FILE="main.tex"
BIB_FILE="refs.bib"
CSL_FILE="gb7714-2015-numeric.csl"
REF_DOC=""
OUTPUT="main_pandoc.docx"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# ==================== 参数解析 ====================
while [[ $# -gt 0 ]]; do
  case $1 in
    --tex)     TEX_FILE="$2"; shift 2 ;;
    --bib)     BIB_FILE="$2"; shift 2 ;;
    --csl)     CSL_FILE="$2"; shift 2 ;;
    --ref-doc) REF_DOC="$2"; shift 2 ;;
    --output)  OUTPUT="$2"; shift 2 ;;
    -h|--help)
      echo "用法: export.sh [--tex FILE] [--bib FILE] [--csl FILE] [--ref-doc FILE] [--output FILE]"
      exit 0 ;;
    *) echo "未知参数: $1"; exit 1 ;;
  esac
done

# ==================== 前置检查 ====================
echo "=========================================="
echo "Pandoc Citeproc Export"
echo "=========================================="

ERRORS=0

echo "[检查] TeX 文件: $TEX_FILE"
if [ ! -f "$TEX_FILE" ]; then
  echo "  ✗ 文件不存在"; ERRORS=$((ERRORS+1))
fi

echo "[检查] Bib 文件: $BIB_FILE"
if [ ! -f "$BIB_FILE" ]; then
  echo "  ✗ 文件不存在"; ERRORS=$((ERRORS+1))
fi

echo "[检查] CSL 文件: $CSL_FILE"
if [ ! -f "$CSL_FILE" ]; then
  echo "  ✗ 文件不存在"; ERRORS=$((ERRORS+1))
fi

echo "[检查] pandoc 版本"
if ! command -v pandoc &> /dev/null; then
  echo "  ✗ pandoc 未安装"; ERRORS=$((ERRORS+1))
else
  echo "  $(pandoc --version | head -1)"
fi

if [ $ERRORS -gt 0 ]; then
  echo ""
  echo "✗ 前置检查失败（$ERRORS 项错误），终止导出"
  exit 1
fi

# ==================== 构建 pandoc 命令 ====================
PANDOC_ARGS=(
  "$TEX_FILE"
  -o "$OUTPUT"
  --top-level-division=section
  --number-sections
  --bibliography="$BIB_FILE"
  --citeproc
  --csl="$CSL_FILE"
)

if [ -n "$REF_DOC" ] && [ -f "$REF_DOC" ]; then
  echo "[检查] 模板文件: $REF_DOC"
  PANDOC_ARGS+=(--reference-doc="$REF_DOC")
fi

# ==================== 导出 ====================
echo ""
echo "[1/4] Pandoc 导出..."
pandoc "${PANDOC_ARGS[@]}" 2>&1 | grep -i "error" && { echo "✗ Pandoc 导出失败"; exit 1; } || true

if [ ! -f "$OUTPUT" ]; then
  echo "✗ 输出文件未生成"
  exit 1
fi

# ==================== 标题样式映射 ====================
echo "[2/4] 标题样式映射..."
STYLE_SCRIPT="$SKILL_DIR/scripts/fix_docx_styles.py"
if [ -f "$STYLE_SCRIPT" ]; then
  if [ -n "$REF_DOC" ]; then
    python3 "$STYLE_SCRIPT" "$OUTPUT"
  else
    echo "  跳过（未指定 --ref-doc 模板）"
  fi
else
  echo "  跳过（fix_docx_styles.py 不存在）"
fi

# ==================== 中英文后处理 ====================
echo "[3/4] 中英文参考文献后处理..."
CN_REFS_SCRIPT="$SKILL_DIR/scripts/fix_cn_refs.py"
if [ ! -f "$CN_REFS_SCRIPT" ]; then
  # fallback: 搜索项目目录下的同名脚本
  LOCAL_SCRIPT=$(find . -maxdepth 2 -name "fix_cn_refs.py" -type f 2>/dev/null | head -1)
  if [ -n "$LOCAL_SCRIPT" ]; then
    CN_REFS_SCRIPT="$LOCAL_SCRIPT"
    echo "  使用项目本地脚本: $CN_REFS_SCRIPT"
  else
    echo "  ⚠ fix_cn_refs.py 未找到，跳过中英文后处理"
    CN_REFS_SCRIPT=""
  fi
fi
if [ -n "$CN_REFS_SCRIPT" ]; then
  python3 "$CN_REFS_SCRIPT" "$OUTPUT" || echo "  ⚠ 中英文后处理执行失败，继续验证"
fi

# ==================== 验证 ====================
echo "[4/4] 验证输出..."
ls -lh "$OUTPUT"
REF_COUNT=$(pandoc "$OUTPUT" -t plain 2>/dev/null | grep -cE '^\[[0-9]+\]' || true)
echo "  参考文献条目数: $REF_COUNT"

echo ""
echo "=========================================="
echo "导出完成: $OUTPUT"
echo "=========================================="
