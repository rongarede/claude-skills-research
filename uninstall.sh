#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$SCRIPT_DIR/skills"
TARGET_DIR="${CLAUDE_SKILLS_DIR:-$HOME/.claude/skills}"

removed=0
skipped=0

for skill_dir in "$SKILLS_DIR"/*/; do
  skill_name="$(basename "$skill_dir")"
  target="$TARGET_DIR/$skill_name"

  if [ -L "$target" ]; then
    link_target="$(readlink "$target")"
    if [[ "$link_target" == "$skill_dir"* ]] || [[ "$link_target" == "$SKILLS_DIR/$skill_name"* ]]; then
      rm "$target"
      echo "  OK    removed $skill_name"
      removed=$((removed + 1))
    else
      echo "  SKIP  $skill_name (symlink points elsewhere)"
      skipped=$((skipped + 1))
    fi
  else
    echo "  SKIP  $skill_name (not a symlink from this repo)"
    skipped=$((skipped + 1))
  fi
done

echo ""
echo "Done: $removed removed, $skipped skipped"
