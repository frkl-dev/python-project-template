default:
    @just --list

# sync license/license_data/spdx_licenses/ with the upstream SPDX license list
# (only adds licenses that are missing; set UPDATE_EXISTING in the script to refresh all)
update-spdx-licenses:
    uv run --no-project --with requests python ./license/update_spdx.py

create-test-project-with-license license_ids_comma_separated:
    bash ./scripts/create_test_project.sh {{license_ids_comma_separated}}

# lint the template's own python machinery (config: ruff.toml). The *rendered*
# project files are linted by the generated projects themselves.
lint-self:
    uvx ruff check license/ misc/
