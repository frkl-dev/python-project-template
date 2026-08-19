# update_spdx.py
#
# Copyright (c) 2023 - 2025 Marius Zwicker
# Copyright (c) 2025 Markus Binsteiner
# All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

'''
Helper to automatically pull and sync the list of available SPDX licenses
from https://github.com/spdx/license-list-data and documented at
https://github.com/spdx/license-list-data/blob/main/accessingLicenses.md#programmatically-accessing-the-online-license-list-using-json
'''

import pathlib
import re
import textwrap

import requests

INCLUDE_NON_OSI = True
UPDATE_EXISTING = False
REQUEST_TIMEOUT = 30  # seconds

LICENSE_LIST_DATA_REPO = 'https://github.com/spdx/license-list-data'
SPDX_FOLDER = pathlib.Path(__file__).parent / 'license_data/spdx_licenses'
BLACKLIST = {
    'CPAL-1.0',  # using too many variables to be added automatically
    'CUA-OPL-1.0',
    'LPPL-1.3c',
    'MPL-1.0',
    'MPL-1.1',
    'RPSL-1.0',
    'SISSL',
    'SPL-1.0',
    'MulanPSL-2.0',
    'OCLC-2.0',
}


def fetch_json(url: str) -> requests.Response:
    '''GET a URL, failing loudly on HTTP errors instead of on the .json() call.'''
    response = requests.get(url, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    return response


def replace_var_tags(string: str) -> str:
    '''Replaces <<var;...>> tags with placeholder text'''
    # Pattern to match <<var;name="...";original="...";match="...">>
    pattern = r'<<var;[^>]+>>'

    def replacer(match):
        var_tag = match.group(0)
        # Try to extract the original value if present
        original_match = re.search(r'original="([^"]+)"', var_tag)
        if original_match:
            return original_match.group(1)
        # Otherwise return a generic placeholder based on the name
        name_match = re.search(r'name="([^"]+)"', var_tag)
        if name_match:
            name = name_match.group(1)
            if name == 'copyright':
                return '[yyyy] [name of copyright owner]'
            return f'[{name}]'
        return '[...]'

    return re.sub(pattern, replacer, string)


def filter_tags(line: str) -> bool:
    '''Returns false if a copyright or tag line'''
    if line.lower().startswith('copyright'):
        return False
    return not (line.startswith('<<') and line.endswith('>>'))


def replace_tags(string: str, replacement: str = '') -> str:
    '''Replaces <<beginOptional>>...<<endOptional>> tags'''
    i = 0
    while i < len(string):
        i = string.find('<<begin', i)
        if i < 0:
            break
        j = string.find('<<end', i)
        if j < 0:
            break
        j = string.find('>>', j) + 2
        string = string[:i] + replacement + string[j:]
    return string


def pad_url(string: str) -> str:
    '''Pads urls to obtain a license'''
    if string.startswith('http'):
        return f'\n    {string.strip()}\n'
    return string


def build_header(detail: dict) -> list[str]:
    '''Derive the header.txt lines from a license's details.'''
    header = detail.get('standardLicenseHeaderTemplate', None)
    if not header:
        header = detail.get('standardLicenseHeader', None)
    if not header:
        # no standard header defined, use name
        return [f"Licensed under the {detail['name']}"]

    header = header.strip('"\n\r')
    header = replace_var_tags(header)
    header = header.split('\n')
    header = [h for h in header if filter_tags(h) and h]
    header = [replace_tags(h) for h in header]
    header = ['\n'.join(textwrap.wrap(h, 72)) + '\n' if len(h) > 72 else h for h in header]
    header = [pad_url(h) for h in header]
    return header


def sync_license(license_info: dict) -> None:
    '''Sync one entry of the upstream license list into SPDX_FOLDER.'''
    license_id = license_info['licenseId']
    if license_id in BLACKLIST:
        return

    license_folder = SPDX_FOLDER / license_id
    license_details_file = license_folder / 'details.json'

    license_header_file = license_folder / 'header.txt'
    if license_header_file.exists() and license_header_file.read_text() and not UPDATE_EXISTING:
        # retain existing headers
        return

    osi = license_info.get('isOsiApproved', True)
    deprecated = license_info.get('isDeprecatedLicenseId', False)
    if not (osi or INCLUDE_NON_OSI) or deprecated:
        return

    detail_obj = fetch_json(f'{LICENSE_LIST_DATA_REPO}/raw/main/json/details/{license_id}.json')
    detail = detail_obj.json()
    header = build_header(detail)

    print(f"-- {license_id}")
    license_folder.mkdir(parents=True, exist_ok=True)

    if not license_details_file.exists() or license_details_file.read_text() != detail_obj.text:
        license_details_file.write_text(detail_obj.text)

    license_text = detail['licenseText']
    license_text_file = license_folder / 'license.txt'
    if not license_text_file.exists() or license_text_file.read_text() != license_text:
        license_text_file.write_text(license_text)

    license_header_file.write_text('\n'.join(header).strip() + '\n')


def main() -> None:
    licenses = fetch_json(f'{LICENSE_LIST_DATA_REPO}/raw/main/json/licenses.json').json()
    for license_info in licenses['licenses']:
        sync_license(license_info)


if __name__ == '__main__':
    main()
