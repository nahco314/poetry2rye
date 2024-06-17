import os
import subprocess
from pathlib import Path

import pytest

from typing import Callable


@pytest.fixture
def dirs() -> Path:
    this_file_path = Path(__file__)
    return this_file_path.parent / "test-dirs"


@pytest.fixture
def rye() -> str:
    return f"{os.getenv("HOME")}/.rye/shims/rye"
