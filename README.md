# My Python project template

This repository contains my template for how I like to have my Python projects setup.
    
## Features

- uses [uv](https://astral.sh/uv) for managing Python and dependencies
- uses [hatch](https://hatch.pypa.io/latest/) (for now) for building and publishing
  - incl. versioning via git tags
- includes CI/CD configuration for:
  - running tests, linting, and typechecking
  - building Python wheels/sdists & conda packages
  - publishing to PyPI
  - publishing to Anaconda (optional)
- a [`justfile`](https://github.com/casey/just) for running common tasks

