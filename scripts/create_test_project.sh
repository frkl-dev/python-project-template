#!/usr/bin/env bash

project_licenses=$1
set -euxo pipefail

rm -rf /tmp/test_project

copier copy --data "full_name=Markus Binsteiner" \
                 --data "email=markus@frkl.dev"\
                 --data "github_user=makkus" \
                 --data "project_licenses=[${project_licenses}]" \
                 --data "project_name=test_project" \
                 --data "project_short_description=A test project." \
                 --data "anaconda_user=freckles" \
                 -T --vcs-ref=HEAD --trust \
                 /var/home/markus/projects/my-setup/my-templates/python-template/ \
                 /tmp/test_project
