# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Copier template for Python projects. It generates complete Python development environments with uv, hatch, pre-commit, and CI/CD workflows.

## Template Development Commands

```bash
just download-license <license_ids>  # Download SPDX license data (e.g., MIT, Apache-2.0)
```

To test template generation:
```bash
copier copy . /path/to/new-project
```

## Generated Project Commands

Projects created from this template use:
```bash
just typecheck        # ty check on src/
just lint             # ruff check with auto-fix
just format           # ruff format
just tests            # pytest tests -s
just test <pattern>   # pytest -k <pattern>
```

## Architecture

**Template processing flow:**
1. `copier.yml` → Main config, includes `copier-tasks.yml`, `copier-copyright.yml`, `copier-messages.yml`
2. `project-files/` → Jinja2 templates (`.jinja` suffix) copied to target
3. Custom Jinja extensions provide template helpers

**Custom Jinja extensions:**
- `misc/jinja_extensions.py`: `current_year` global, `render_template` filter
- `license/jinja_license_extensions.py`: `{% license_text %}`, `{% license_list %}`, `{% license_header %}` tags for SPDX license handling

**License system:**
- `license/license_data/spdx_licenses/` contains downloaded license data (details.json, license.txt, header.txt per license)
- `DEFAULT_LICENSES` in `jinja_license_extensions.py` controls which licenses appear in selection

**Post-copy tasks** (`copier-tasks.yml`):
- Initializes git with `develop` branch
- Installs pre-commit hooks (including commit-msg for commitlint)
- Runs pre-commit on all files
- Creates initial commit

## Build System

Generated projects use:
- **uv**: Dependency management
- **hatchling** + **uv-dynamic-versioning**: Build backend with git tag versioning
- **pre-commit**: ruff, ty, commitlint, license-tools, pyupgrade
- Commits to `main` branch are blocked by pre-commit