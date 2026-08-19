# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Copier template for Python projects. It generates complete Python development environments with uv, hatch, pre-commit, and CI/CD workflows.

## Template Development Commands

```bash
just update-spdx-licenses  # sync license/license_data/spdx_licenses/ with the upstream SPDX list
```

To test template generation:
```bash
copier copy . /path/to/new-project --trust
```
Note that Copier's `-T` is `--skip-tasks`, not `--trust`; passing it skips git init and leaves the
generated project unbuildable (versions come from git tags).

## Generated Project Commands

Projects created from this template use:
```bash
just typecheck        # pyrefly check (just typecheck-ty for ty)
just lint             # ruff check with auto-fix
just format           # ruff format
just tests            # pytest tests -s
just test <pattern>   # pytest -k <pattern>
just build-conda      # rattler-build (only when anaconda_user is set)
```

## Conda packaging

Generated projects get a [rattler-build](https://rattler.build) recipe at
`conda.recipe/recipe.yaml` (template: `project-files/conda.recipe/recipe.yaml.jinja`), built and
published by the `build_conda_package` / `release_conda_package` jobs in
`build-linux.yaml.jinja`. `noarch: python`, so linux builds it once for every platform.

The whole thing is gated on `anaconda_user`: the workflow jobs sit behind `{% if anaconda_user %}`,
and `copier.yml`'s `_exclude` drops `conda.recipe/` entirely when the answer is empty.

Three non-obvious things, all of which are load-bearing:

- **The recipe packages the wheel, not the source.** rattler-build does not copy `.git` into the
  build sandbox, so building from source would make `uv-dynamic-versioning` fall back to
  `fallback-version = "0.0.0"` while the recipe metadata claims the real version. Instead the
  conda job depends on `build_python_package`, downloads the `build-dists` artifact, and derives
  `PKG_VERSION` from the wheel filename; the recipe reads it via `env.get("PKG_VERSION")`.
  `just build-conda` does the same thing locally, which is why it runs `uv build` first.
- **`use_gitignore: false` on the `../dist` source.** `uv build` writes a `dist/.gitignore`
  containing `*`, so rattler-build's default would skip the directory and the build script would
  find no wheel.
- **`LICENSES/` is pulled in as a second source.** `about.license_file` resolves against the work
  directory, not the recipe directory, so `../LICENSES/<ID>.txt` silently copies nothing and the
  build fails with "No license files were copied".

Runtime dependencies are **not** derived from `pyproject.toml` -- `requirements.run` has to be
maintained by hand. The generated `TODO.md`, `CLAUDE.md` and `AGENTS.md` all say so.

## Python version handling

There is exactly one question -- `python_min_version` -- and everything else is derived from it,
so the supported range cannot drift. `copier.yml` defines:

- `known_python_versions` (`when: false`) -- the list of versions the template knows about. This
  is the single place to edit when a new Python ships; it feeds the prompt's `choices`.
- `python_versions` -- `known_python_versions` sliced from the chosen minimum upwards.
- `python_max_version` -- the newest supported version.
- `python_min_tag` -- `py310`-style spelling.

Consumers, all of which must stay derived rather than hardcoded:

| Where | Uses |
| --- | --- |
| `pyproject.toml.jinja` `requires-python`, `[tool.pixi.dependencies].python` | `python_min_version` |
| `pyproject.toml.jinja` classifiers | loop over `python_versions` |
| `pyproject.toml.jinja` ruff `target-version`, pyupgrade `--pyXY-plus` arg | `python_min_tag` |
| `build-{linux,darwin,windows}.yaml.jinja` matrices (4 of them) | `python_versions` piped through `tojson` |
| `setup-uv-env/action.yaml.jinja` default | `python_max_version` |
| `conda.recipe/recipe.yaml.jinja` `context.python_min` | `python_min_version` |

Only `python_min_version` is written to `.copier-answers.yml`; the derived values are recomputed
on every render. That means extending `known_python_versions` here automatically widens the CI
matrix and classifiers of existing projects on their next `copier update`.

**The floor is 3.10, deliberately.** The generated `src/**/__init__.py` uses PEP 604 unions
(`IO[str] | None`) in function signatures, which are evaluated at def time and raise a TypeError
on 3.9 -- the old `requires-python = ">=3.9"` was never actually true. Anything added to
`known_python_versions` has to be able to import the generated package.

`[tool.pyrefly]` deliberately leaves `python-version` unset so each leg of the CI matrix checks
the interpreter it actually runs on.

Note `scripts/create_test_project.sh` passes `--defaults`, so adding a new question with a
sensible default does not break the non-interactive test render.

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

## Development

For development, you can create a test project with a specific license using the following command:
```bash
just create-test-project-with-license <license_ids_comma_separated>
```
Replace `<license_ids_comma_separated>` with the desired license IDs separated by commas. The resulting project will live under `/tmp/test_project`.

## Build System

Generated projects use:
- **uv**: Dependency management
- **hatchling** + **uv-dynamic-versioning**: Build backend with git tag versioning
- **pre-commit**: ruff, pyrefly, commitlint, license-tools, pyupgrade
- **rattler-build**: conda packages (optional, see above)
- Commits to `main` branch are blocked by pre-commit

## Things to keep in sync

- `justfile.jinja` and `Makefile.jinja` expose the same task set. Note the shell `$(...)` in
  `build-conda` has to be written `$$(...)` in the Makefile, since make claims a single `$`.
- ruff's `target-version` and pyupgrade's `--pyXY-plus` both come from `python_min_tag`; if they
  ever diverge the two tools fight over the same files.
- The ruff version is pinned in two places: the `ruff-pre-commit` `rev` in
  `.pre-commit-config.yaml.jinja` and the `ruff-action` `version` in `build-linux.yaml.jinja`.
  If they drift, the hook and CI disagree about what is clean. (The `ruff` dev dependency is
  deliberately unpinned and can run ahead.)
- `CLAUDE.md.jinja` and `AGENTS.md.jinja` differ only in the title and first line.
- The `prefix-dev/rattler-build-action` pin appears twice in `build-linux.yaml.jinja` (the build
  job and the `setup-only` step in the release job).

## Delimiter collisions

`_templates_suffix: .jinja` means only `.jinja` files are rendered, and undefined variables render
as the empty string rather than erroring -- so a missed escape produces silently-broken output
instead of a failed render. Anything meant to reach the generated project must be wrapped in
`{% raw %}...{% endraw %}`:

- GitHub Actions `${{ matrix.python_version }}` and `${{ secrets.* }}` in the workflows.
- `just` recipe parameters, e.g. `{{pattern}}` in `justfile.jinja`.
- **rattler-build expressions** in `conda.recipe/recipe.yaml.jinja` -- it uses the same `${{ ... }}`
  syntax, so that file is one big raw block that steps out only for Copier values.

Always re-render and read the output rather than trusting the template to read correctly.
