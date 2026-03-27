#!/usr/bin/env python3
"""共享文件查找工具函数"""

from pathlib import Path


def find_json_files(paths: list[str]) -> list[Path]:
    """从路径参数中解析出所有 raw JSON 文件

    支持目录（自动扫描 layer_*_raw.json）和单个 JSON 文件路径。
    """
    files: list[Path] = []
    for p in paths:
        path = Path(p)
        if path.is_dir():
            files.extend(sorted(path.glob("layer_*_raw.json")))
        elif path.is_file() and path.suffix == ".json":
            files.append(path)
    return files
