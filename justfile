default:
    @just --list

download-license *license_ids:
    uvx  python ./license/license_downloader.py  ./license/license_data {{license_ids}}
