#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
TARGET_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

mkdir -p "$TARGET_DIR"

installed=0
skipped=0

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  target="$TARGET_DIR/$skill_name"

  if [ -e "$target" ]; then
    echo "  SKIP  $skill_name (already exists)"
    skipped=$((skipped + 1))
  else
    ln -s "$skill_dir" "$target"
    echo "  OK    $skill_name"
    installed=$((installed + 1))
  fi
done

echo ""
echo "Done: $installed installed, $skipped skipped"
