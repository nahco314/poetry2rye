import os
import subprocess
from pathlib import Path

import pytest

from poetry2rye.main import main as app_main

import shutil
import filecmp
import difflib


# @pytest.mark.parametrize(("project_name",), [("p2",)])
# @pytest.mark.parametrize(("project_name",), [("p0",)])
@pytest.mark.parametrize(("project_name",), [("p0",), ("p1",), ("p2",)])
def test_migrate(project_name: str, tmp_path: Path, dirs: Path, rye: str) -> None:
    base_project = dirs / project_name
    tmp_project = tmp_path / project_name

    shutil.copytree(base_project, tmp_project)

    app_main(["mig", str(tmp_project.absolute())])

    subprocess.run([rye, "sync"], cwd=tmp_project, check=True)

    assert (
        filecmp.dircmp(dirs / f"mig-{project_name}/src", tmp_project / "src").diff_files
        == []
    )
    expected_pyproject_toml = dirs / f"mig-{project_name}/pyproject.toml"
    tmp_pyproject_toml = tmp_project / "pyproject.toml"
    print(tmp_pyproject_toml.as_posix())

    _replace_crlf(expected_pyproject_toml)
    _replace_crlf(tmp_pyproject_toml)
    vv = difflib.unified_diff(
        expected_pyproject_toml.read_text().splitlines(),
        tmp_pyproject_toml.read_text().splitlines(),
    )
    assert tmp_pyproject_toml.read_text() == expected_pyproject_toml.read_text()
    vv = list(vv)
    assert vv == []

    # assert _stat_sig(left_file) == _stat_sig(right_file)
    assert filecmp.cmp(
        dirs / f"mig-{project_name}/pyproject.toml",
        tmp_project / "pyproject.toml",
        False,
    )


# # type, size, mtime
# def _stat_sig(p: Path) -> str:
#     return f"{p.stat().st_mode} {p.stat().st_size} {p.stat().st_mtime}"


def _replace_crlf(infile: Path):
    # if not windows, do nothing
    if os.name != "nt":
        return

    windows_line_ending = b"\r\n"
    unix_line_ending = b"\n"

    content = infile.read_bytes()

    # Windows ➡ Unix
    content = content.replace(windows_line_ending, unix_line_ending)

    infile.write_bytes(content)
