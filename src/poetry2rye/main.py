import argparse
import shutil
from pathlib import Path

from poetry2rye.convert import convert
from poetry2rye.utils import backup_path
from poetry2rye.utils import get_biggest_backup_num


def main():
    parser = argparse.ArgumentParser(
        prog="poetry2rye",
        description="A simple tool to migrate your Poetry project to rye",
    )
    parser.add_argument("-p", "--path", default="./")
    parser.add_argument("--get-backup", nargs="?", const="-1", default="")

    args = parser.parse_args()

    project_path = Path(args.path).absolute()
    get_backup = args.get_backup

    if get_backup == "":
        convert(project_path)

        print("done")
    else:
        num = int(get_backup)
        if num == -1:
            num = get_biggest_backup_num(project_path)

        assert num >= 0

        path = backup_path(project_path, num)

        assert path.exists()

        c = input(f"really restore backup from {path}? [y/N] ")

        if c != "y":
            print("aborting...")
            return

        print("restoring backup...")

        shutil.rmtree(project_path)
        shutil.copytree(path, project_path)

        print("done")


if __name__ == "__main__":
    main()
