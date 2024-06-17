import subprocess
from pathlib import Path

import pytest

from poetry2rye.main import main as app_main

import shutil
import filecmp


@pytest.mark.parametrize(("project_name",), [("p0",), ("p1",)])
def test_backup(project_name: str, tmp_path: Path, dirs: Path, rye: str) -> None:
    base_project = dirs / project_name
    tmp_project = tmp_path / project_name

    shutil.copytree(base_project, tmp_project)

    app_main(["mig", str(tmp_project.absolute())])

    app_main(["get-backup", str(tmp_project.absolute()), "-y"])

    assert filecmp.dircmp(base_project, tmp_project).diff_files == []
