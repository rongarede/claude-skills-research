#!/bin/bash
# ============================================================
# latex-sentence-surgery: sentence-level minimal edit for LaTeX
# ============================================================

set -euo pipefail

if [[ $# -lt 3 ]]; then
  echo "Usage:"
  echo "  $0 <file> remove <target>"
  echo "  $0 <file> replace <target> <replacement>"
  exit 1
fi

FILE="$1"
MODE="$2"
TARGET="$3"
REPLACEMENT="${4:-}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$SCRIPT_DIR/sentence_edit.py"

if [[ ! -f "$FILE" ]]; then
  echo "ERROR: file not found: $FILE"
  exit 1
fi

if [[ "$MODE" == "remove" ]]; then
  python3 "$PY" --file "$FILE" --mode remove --target "$TARGET"
elif [[ "$MODE" == "replace" ]]; then
  if [[ $# -lt 4 ]]; then
    echo "ERROR: replacement text is required for mode=replace"
    exit 1
  fi
  python3 "$PY" --file "$FILE" --mode replace --target "$TARGET" --replacement "$REPLACEMENT"
else
  echo "ERROR: mode must be remove or replace"
  exit 1
fi

echo "OK: sentence surgery finished"
