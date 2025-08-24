# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Copier template for Python projects that sets up a complete Python development environment with modern tooling.

## Architecture

The repository structure follows a template-based approach:
- `project-files/`: Contains Jinja2 templates that will be copied to new projects
- `license/`: License management system with SPDX license data and custom extensions
- `misc/`: Custom Jinja extensions for template processing
- Configuration files (`copier.yml`, `copier-*.yml`): Define template variables and tasks

## Key Development Commands

When working on generated projects (not the template itself), use these commands:

### Type Checking
```bash
just typecheck  # Runs ty check on the source code
```

### Linting & Formatting
```bash
just lint    # Run ruff linter with auto-fix
just format  # Format code with ruff
```

### Testing
```bash
just tests           # Run all tests
just test <pattern>  # Run tests matching a pattern
```

### Template-specific Commands
```bash
just download-license <license_ids>  # Download specific SPDX licenses
```

## Build System

Generated projects use:
- **uv**: For Python dependency management and environment handling
- **hatch**: For building and publishing packages
- **hatchling**: Build backend with dynamic versioning from git tags
- **pre-commit**: Automated code quality checks on commit
- **commitlint**: Enforces conventional commit messages

## Template Variables

Key template variables defined in `copier.yml`:
- `project_name`: Human-readable project name
- `project_slug`: Python-safe package name
- `project_base_module`: Base module name (defaults to project_slug)
- `full_name`, `email`: Author information
- `github_user`: GitHub username/organization
- `anaconda_user`: Anaconda username (optional)
- `project_licenses`: List of SPDX license identifiers

## Generated Project Structure

Projects created from this template will have:
- `src/{{project_base_module}}/`: Source code directory
- `tests/`: Test directory
- `pyproject.toml`: Project metadata and dependencies
- `justfile`: Task runner commands
- `commitlint.config.js`: Commit message linting
- Git initialized with develop branch and pre-commit hooks