default:
    @just --list

download-license *license_ids:
    uvx  python ./license/license_downloader.py  ./license/license_data {{license_ids}}

create-test-project-with-license license_ids_comma_separated:
    bash ./scripts/create_test_project.sh {{license_ids_comma_separated}}
