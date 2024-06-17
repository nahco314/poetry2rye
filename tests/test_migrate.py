import subprocess
from pathlib import Path

import pytest

from poetry2rye.main import main as app_main

import shutil
import filecmp


@pytest.mark.parametrize(("project_name",), [("p0",), ("p1",)])
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
    assert filecmp.cmp(
        dirs / f"mig-{project_name}/pyproject.toml", tmp_project / "pyproject.toml"
    )
