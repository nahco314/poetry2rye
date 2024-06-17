import re
from abc import abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from typing import Optional

import pyproject_parser
import slugify
from poetry.core.constraints.version.parser import parse_constraint
from poetry.core.constraints.version.version_constraint import VersionConstraint
from poetry.core.version.helpers import format_python_constraint

from poetry2rye.error import ControlledError
from poetry2rye.utils import find_other_key


# unused
def poetry_canonicalize_name(project_name: str) -> str:
    """
    Convert a project name to a canonical form by Poetry-Style.
    """
    return re.sub(r"[-_.]+", "-", project_name).lower()


# memo: How does Poetry decide on module names?


def rye_canonicalize_name(project_name: str) -> str:
    return slugify.slugify(project_name)


def rye_module_name(project_name: str) -> str:
    return rye_canonicalize_name(project_name).replace("-", "_")


@dataclass
class Dependency:
    name: str
    is_dev: bool

    def is_python_dep(self) -> bool:
        return False

    @abstractmethod
    def to_str(self) -> str:
        raise NotImplementedError


@dataclass
class BasicDependency(Dependency):
    version: VersionConstraint
    extras: Optional[list[str]]

    def is_python_dep(self) -> bool:
        return self.name == "python"

    def to_str(self) -> str:
        return f"{self.name}{format_python_constraint(self.version)}"


@dataclass
class GitDependency(Dependency):
    git_link: str

    def to_str(self) -> str:
        return f"{self.name} @ git+{self.git_link}"


class PoetryProject:
    def __init__(self, project_path: Path) -> None:
        self.path = project_path
        self.project_name = rye_canonicalize_name(self.path.name)
        self.module_name = rye_module_name(self.path.name)

        if not (self.path / "pyproject.toml").exists():
            raise ControlledError("pyproject.toml not found")

        self.pyproject = pyproject_parser.PyProject.load(self.path / "pyproject.toml")
        self.poetry = self.pyproject.tool["poetry"]

        if self.pyproject.project is not None:
            raise ControlledError(
                "this pyproject.toml has a project section.\n"
                "for now, poetry2rye only supports pyproject.toml written using "
                "tool.poetry. this may change in the future."
            )

        if self.poetry is None:
            raise ControlledError("poetry section not found in pyproject.toml")

        self.src_path: Path
        self.module_path: Path
        # this method is not exact, but tentatively we do this
        if (self.path / "src").exists():
            self.src_path = self.path / "src"
            sub_lst = list(self.src_path.iterdir())
            if len(sub_lst) == 1:
                self.src_path = sub_lst[0]
            elif len(sub_lst) == 0:
                raise ControlledError("no subdirectories found in src")
            else:
                raise ControlledError("multiple subdirectories found in src")
        else:
            self.src_path = self.path
            self.module_path = self.src_path / self.module_name

            if not self.module_path.exists():
                raise ControlledError("module not found")

    def process_dependencies_dict(
        self, dct: dict[str, Any], is_dev: bool
    ) -> list[Dependency]:
        res = []

        for name, item in dct.items():
            if isinstance(item, str):
                res.append(
                    BasicDependency(
                        name=name,
                        version=parse_constraint(item),
                        extras=None,
                        is_dev=is_dev,
                    )
                )
            else:
                assert isinstance(item, dict)

                if "git" in item:
                    if (k := find_other_key(item, ["git"])) is not None:
                        raise ControlledError(
                            f"key {k} is not supported (in dependency {name})"
                        )

                    res.append(
                        GitDependency(name=name, git_link=item["git"], is_dev=is_dev)
                    )

                elif "version" in item:
                    if (k := find_other_key(item, ["version"])) is not None:
                        raise ControlledError(
                            f"key {k} is not supported (in dependency {name})"
                        )

                    res.append(
                        BasicDependency(
                            name=name,
                            version=parse_constraint(item["version"]),
                            extras=None,
                            is_dev=is_dev,
                        )
                    )

                else:
                    raise ControlledError(
                        f"unsupported dependency type (in dependency {name})"
                    )

        return res

    @property
    def dependencies(self) -> list[Dependency]:
        res = []

        dep = self.poetry["dependencies"]
        if dep is not None:
            res.extend(self.process_dependencies_dict(dep, is_dev=False))

        try:
            dev_dep = self.poetry["group"]["dev"]["dependencies"]
        except KeyError:
            dev_dep = None
        if dev_dep is not None:
            res.extend(self.process_dependencies_dict(dev_dep, is_dev=True))

        return res
