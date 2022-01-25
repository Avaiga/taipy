from pathlib import Path
import typing as t


def _get_non_existent_file_path(dir_path: Path, file_name: str) -> Path:
    if not file_name:
        file_name = "taipy_file.bin"
    file_path = dir_path / file_name
    if file_path.exists():
        return __get_new_file_name(dir_path, file_path.stem, 0, file_path.suffix)
    else:
        return file_path


def __get_new_file_name(dir_path: Path, file_stem: str, index: int, ext: str) -> Path:
    file_path = dir_path / f"{file_stem}.{index}{ext}"
    if file_path.exists():
        return __get_new_file_name(dir_path, file_stem, index + 1, ext)
    return file_path
