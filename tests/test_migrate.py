import os
import subprocess
from pathlib import Path

import pytest
import shutil
import filecmp
import difflib

from poetry2rye.main import main as app_main

PROJECT_NAMES = ["p0", "p1", "p2"]


@pytest.mark.parametrize("project_name", PROJECT_NAMES)
def test_migrate(project_name: str, tmp_path: Path, dirs: Path, rye: str) -> None:
    base_project = dirs / project_name
    tmp_project = tmp_path / project_name
    mig_project = dirs / f"mig-{project_name}"

    shutil.copytree(base_project, tmp_project)

    app_main(["mig", str(tmp_project.absolute())])

    subprocess.run([rye, "sync"], cwd=tmp_project, check=True)

    assert_directories_equal(mig_project / "src", tmp_project / "src")
    assert_pyproject_toml_equal(mig_project, tmp_project)


def assert_directories_equal(expected_dir: Path, actual_dir: Path) -> None:
    assert filecmp.dircmp(expected_dir, actual_dir).diff_files == []


def assert_pyproject_toml_equal(expected_dir: Path, actual_dir: Path) -> None:
    expected_pyproject = expected_dir / "pyproject.toml"
    actual_pyproject = actual_dir / "pyproject.toml"

    normalize_line_endings(expected_pyproject)
    normalize_line_endings(actual_pyproject)

    expected_content = expected_pyproject.read_text()
    actual_content = actual_pyproject.read_text()

    msg = (
        f"pyproject.toml contents differ:\n"
        f"{''.join(difflib.unified_diff(expected_content.splitlines(keepends=True), actual_content.splitlines(keepends=True)))}"
    )
    assert actual_content == expected_content, msg

    msg = (
        f"pyproject.toml files are not identical:\n"
        f"{expected_pyproject}\n{actual_pyproject}"
    )
    assert filecmp.cmp(expected_pyproject, actual_pyproject, shallow=False), msg


def normalize_line_endings(file_path: Path) -> None:
    if os.name == "nt":
        content = file_path.read_bytes()
        normalized_content = content.replace(b"\r\n", b"\n")
        file_path.write_bytes(normalized_content)
