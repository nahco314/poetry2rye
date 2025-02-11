# poetry2rye

A simple tool to migrate your Poetry project to rye.

# Install
```commandline
rye install poetry2rye
```

# Usage
### Migrate
`poetry2rye mig [PATH]`

Migrate path projects to rye.

This command does the following:
- if the project is flat-layout, make it src-layout
- remove poetry.lock
  - this doesn't respect the lock file (at this time)
- change pyproject.toml
  - remove `[tool.poetry]` and `[tool.poetry.*]`
  - make `[project]` from `[tool.poetry]` and `[tool.poetry.*]`
  - change `[build-system]`
  - add `[tool.rye]`
  - add `[tool.hatch.metadata]`

#### Options
- `--ignore-src` : use this flag to ignore creating `src/` directory, so it won't change the project files layout.
- `--virtual` : use this command to consider project as a [virtual project](https://rye.astral.sh/guide/virtual/) (based on rye docs).
> Virtual projects are projects which are themselves not installable Python packages, but that will sync their dependencies. 


See full options with their descriptions with `poetry2rye mig --help` command,


### Get Backup
`poetry2rye get-backup [PATH]`

Options:
- `-n [NUMBER]`: The number of the backup to retrieve. If not specified, the last backup created will be used.
- `-y`: Skip the confirmation prompt.

Retrieve the backup automatically created during migration and replace the project with the backup.

if NUMBER is not specified, the last backup created will be used.

The backup folder is `.__p2r_backup_{project_name}_{number}` format and placed in the same directory as the project directory (which is a child of the project parent directory).

## Dockerfile
Since this tool does not support migration for `Dockerfile` (which is not rational to add), you've to migrate your `Dockerfile` **manually** based on [rye documentation](https://rye.astral.sh/guide/docker/)

# Other
This tool is for personal use and should be used at your own risk. Backups will be made, but we cannot be held responsible for project corruption!

The license is the MIT License.

If you have any bugs, mistakes, feature suggestions, etc., issues and pull requests are welcome.
