#!/usr/bin/env bash

project_licenses=$1
set -euxo pipefail

# Resolve the template root from this script's location rather than hardcoding it, so
# the script also works from a git worktree (e.g. a feature branch checked out beside
# the main clone).
template_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

rm -rf /tmp/test_project

copier copy --data "full_name=Markus Binsteiner" \
                 --data "email=markus@frkl.dev"\
                 --data "github_user=makkus" \
                 --data "project_licenses=[${project_licenses}]" \
                 --data "project_name=test_project" \
                 --data "project_short_description=A test project." \
                 --data "anaconda_user=freckles" \
                 --vcs-ref=HEAD --trust --defaults \
                 "${template_dir}" \
                 /tmp/test_project
