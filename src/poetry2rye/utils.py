import re
from pathlib import Path
from typing import Optional


def backup_path(project_path: Path, num: int) -> Path:
    return project_path.parent / f".__p2r_backup_{project_path.name}_{num}"


def as_backup_path(project_path: Path, backup_path: Path) -> Optional[int]:
    m = re.match(r"\.__p2r_backup_(.+)_(\d+)", backup_path.name)
    if m and project_path.name == m.group(1):
        return int(m.group(2))
    return None


def is_not_none(x: object) -> bool:
    return x is not None


def get_biggest_backup_num(project_path: Path) -> Optional[int]:
    return max(
        filter(
            is_not_none,
            (
                as_backup_path(project_path, bro)
                for bro in project_path.parent.iterdir()
            ),
        ),
        default=None,
    )


def get_next_backup_path(project_path: Path) -> Path:
    biggest = get_biggest_backup_num(project_path)
    return backup_path(project_path, biggest + 1 if biggest is not None else 0)
