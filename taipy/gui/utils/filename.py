import typing as t
from pathlib import Path


def _get_non_existent_file_path(dir_path: Path, file_name: str) -> Path:
    if not file_name:
        file_name = "taipy_file.bin"
    file_path = dir_path / file_name
    index = 0
    file_stem = file_path.stem
    file_suffix = file_path.suffix
    while file_path.exists():
        file_path = dir_path / f"{file_stem}.{index}{file_suffix}"
        index += 1
    return file_path
