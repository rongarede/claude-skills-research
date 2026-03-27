#!/bin/bash
# ============================================================
# rename.sh - PDF 自动重命名工具
# 用法: rename.sh <PDF文件路径>
# ============================================================

set -e

# ==================== 配置 ====================
ILLEGAL_CHARS='[/\\:*?"<>|]'

# ==================== 帮助信息 ====================
show_help() {
    cat << 'EOF'
PDF 自动重命名工具

用法:
    rename.sh <PDF文件路径>

功能:
    从 PDF 元数据中提取标题，清理非法字符后重命名文件

依赖:
    exiftool 或 pdfinfo（二选一）

示例:
    rename.sh ~/Downloads/paper.pdf
    # 如果标题为 "A Novel Approach"
    # → ~/Downloads/A Novel Approach.pdf
EOF
    exit 0
}

# ==================== 主逻辑 ====================
main() {
    local pdf_path="$1"

    # 帮助信息
    [[ "$pdf_path" == "-h" || "$pdf_path" == "--help" || -z "$pdf_path" ]] && show_help

    # 1. 检查文件存在
    if [[ ! -f "$pdf_path" ]]; then
        echo "❌ 文件不存在: $pdf_path"
        exit 1
    fi

    # 2. 提取标题（优先 exiftool，回退 pdfinfo）
    local title=""
    if command -v exiftool &>/dev/null; then
        title=$(exiftool -Title -s3 "$pdf_path" 2>/dev/null || true)
    elif command -v pdfinfo &>/dev/null; then
        title=$(pdfinfo "$pdf_path" 2>/dev/null | grep "^Title:" | cut -d: -f2- | xargs || true)
    else
        echo "❌ 需要 exiftool 或 pdfinfo"
        echo "   macOS: brew install exiftool"
        echo "   Linux: apt install libimage-exiftool-perl"
        exit 1
    fi

    # 3. 校验标题
    if [[ -z "$title" || "$title" == "(null)" || "$title" == "null" ]]; then
        echo "❌ PDF 无标题元数据"
        exit 1
    fi

    # 4. 清理非法字符
    local clean_title
    clean_title=$(echo "$title" | sed "s/$ILLEGAL_CHARS/-/g")

    # 5. 构建新路径
    local dir
    dir=$(dirname "$pdf_path")
    local new_path="$dir/$clean_title.pdf"

    # 6. 检查目标文件是否已存在
    if [[ -f "$new_path" && "$pdf_path" != "$new_path" ]]; then
        echo "⚠️ 目标文件已存在: $new_path"
        exit 1
    fi

    # 7. 重命名
    if [[ "$pdf_path" == "$new_path" ]]; then
        echo "✓ 文件名已是标题: $clean_title.pdf"
    else
        mv "$pdf_path" "$new_path"
        echo "✓ 已重命名为: $clean_title.pdf"
    fi
}

main "$@"
