# poetry2rye

A simple tool to migrate your Poetry project to rye.

# Install
```commandline
rye install poetry2rye
```

# Usage
### Migrate
`poetry2rye [PATH]`

Migrate path projects to rye. The default of PATH is `.`

This command does the following:
- if the project is flat-layout, make it src-layout
- remove poetry.lock
- change pyproject.toml
  - remove `[tool.poetry]` and `[tool.poetry.*]`
  - make `[project]` from `[tool.poetry]` and `[tool.poetry.*]`
  - change `[build-system]`
  - add `[tool.rye]`
  - add `[tool.hatch.metadata]`

### Get Backup
`poetry2rye [PATH] --get-backup [NUMBER]`

Retrieve the backup automatically created during migration and replace the project with the backup.

if NUMBER is not specified, the last backup created will be used.

The backup folder is `.__p2r_backup_{project_name}_{number}` format and placed in the same directory as the project directory (which is a child of the project parent directory).

# Other
This tool is for personal use and should be used at your own risk. Backups will be made, but we cannot be held responsible for project corruption!

The license is the MIT License.

If you have any bugs, mistakes, feature suggestions, etc., issues and pull requests are welcome.
