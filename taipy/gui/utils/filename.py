from pathlib import Path
import typing as t


def _get_non_existent_file_path(dir_path: Path, file_name: str) -> Path:
    if not file_name:
        file_name = "taipy_file.bin"
    file_path = dir_path / file_name
    index = 0
    while file_path.exists():
        file_path = dir_path / f"{file_path.stem}.{index}{file_path.suffix}"
        index += 1
    return file_path
