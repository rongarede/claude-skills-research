#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""latex-sentence-surgery: edit one target sentence in a text file."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", required=True)
    parser.add_argument("--mode", choices=["remove", "replace"], required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--replacement", default="")
    args = parser.parse_args()

    path = Path(args.file)
    text = path.read_text(encoding="utf-8")

    count = text.count(args.target)
    if count == 0:
        print("ERROR: target sentence not found")
        return 2

    if args.mode == "remove":
        new_text = text.replace(args.target, "", 1)
    else:
        new_text = text.replace(args.target, args.replacement, 1)

    path.write_text(new_text, encoding="utf-8")
    print(f"OK: mode={args.mode}, matched={count}, edited=1")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
