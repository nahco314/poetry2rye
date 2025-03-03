import argparse
import shutil
from pathlib import Path
from typing import Any, Optional

from poetry2rye.convert import convert
from poetry2rye.error import ControlledError
from poetry2rye.utils import backup_path
from poetry2rye.utils import get_biggest_backup_num


def handle_mig(args: Any) -> None:
    path: Path = args.path
    project_path = Path(path).absolute()
    ensure_src: bool = not args.ignore_src
    virtual_project: bool = args.virtual

    convert(
        project_path=project_path,
        ensure_src=ensure_src,
        virtual_project=virtual_project,
    )

    print("done")


def handle_get_backup(args: Any) -> None:
    path = args.path
    num = args.backup_number
    yes = args.yes
    project_path = Path(path).absolute()

    if num is None:
        num = get_biggest_backup_num(project_path)

    assert num >= 0

    path = backup_path(project_path, num)

    assert path.exists()

    if not yes:
        c = input(f"really restore backup from {path}? [y/N] ")

        if c != "y":
            print("aborting...")
            return

    print("restoring backup...")

    shutil.rmtree(project_path)
    shutil.copytree(path, project_path)

    print("done")


def main(args: Optional[list[str]] = None):
    parser = argparse.ArgumentParser(
        prog="poetry2rye",
        description="A simple tool to migrate your Poetry project to rye",
    )

    subparsers = parser.add_subparsers()

    mig_parser = subparsers.add_parser("mig", help="migrate a Poetry project to rye")

    mig_parser.add_argument("path")
    mig_parser.set_defaults(func=handle_mig)

    mig_parser.add_argument(
        "--ignore-src",
        help='use it to ignore the checking/creating "src/" directory during migration process (by default will check and create).',
        action="store_true",
        default=False,
    )
    mig_parser.add_argument(
        "--virtual",
        help="perform migration by considering as a virtual package.\n\nA virtual package can have dependencies but is itself not installed as a Python package.  It also cannot be published.",
        action="store_true",
        default=False,
    )

    get_backup_parser = subparsers.add_parser(
        "get-backup", help="get a backup of a Poetry project"
    )

    get_backup_parser.add_argument("path")
    get_backup_parser.add_argument(
        "--backup-number",
        "-n",
        help="the number of the backup to restore",
        type=int,
        default=None,
    )
    get_backup_parser.add_argument(
        "--yes",
        "-y",
        help="do not ask for confirmation",
        action="store_true",
    )
    get_backup_parser.set_defaults(func=handle_get_backup)

    args = parser.parse_args(args)
    if not hasattr(args, "func"):
        parser.print_help()
        exit(1)

    try:
        args.func(args)
    except ControlledError as e:
        print(f"error: {e}")
        exit(1)
    except Exception:
        print("unexpected error occurred!")
        raise


if __name__ == "__main__":
    main()
