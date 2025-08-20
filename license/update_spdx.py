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
import textwrap
import requests

INCLUDE_NON_OSI = True
UPDATE_EXISTING = False

LICENSE_LIST_DATA_REPO = 'https://github.com/spdx/license-list-data'
SPDX_FOLDER = pathlib.Path(__file__).parent / 'license_data/spdx_licenses'
BLACKLIST = {
    'CPAL-1.0'  # using too many variables to be added automatically
    'CUA-OPL-1.0',
    'LLPL-1.3c',
    'MPL-1.0',
    'MPL-1.1',
    'RPSL-1.0',
    'SISSL',
    'SPL-1.0',
    'MulanPSL-2.0',
    'OCLC-2.0'
}

licenses = requests.get(f'{LICENSE_LIST_DATA_REPO}/raw/main/json/licenses.json')
licenses = licenses.json()

# generate additional licenses
for license in licenses['licenses']:
    id = license['licenseId']
    if id in BLACKLIST:
        continue

    license_folder = SPDX_FOLDER / id
    license_details_file = license_folder / 'details.json'

    license_header_file = license_folder / 'header.txt'
    if license_header_file.exists() and license_header_file.read_text() and not UPDATE_EXISTING:
        # retain existing headers
        continue

    osi = license.get('isOsiApproved', True)
    deprecated = license.get('isDeprecatedLicenseId', False)

    if (osi or INCLUDE_NON_OSI) and not deprecated:
        detail_obj = requests.get(f'{LICENSE_LIST_DATA_REPO}/raw/main/json/details/{id}.json')

        detail = detail_obj.json()
        header = detail.get('standardLicenseHeaderTemplate', None)
        if not header:
            header = detail.get('standardLicenseHeader', None)
        if not header:
            # no standard header defined, use name
            header = [f"Licensed under the {detail['name']}"]
        else:
            header = header.strip('"\n\r')
            
            def replace_var_tags(string):
                '''Replaces <<var;...>> tags with placeholder text'''
                import re
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
            
            # Process var tags first
            header = replace_var_tags(header)
            header = header.split('\n')

            def filter_tags(line):
                '''Returns false if a copyright or tag line'''
                if line.lower().startswith('copyright'):
                    return False
                if line.startswith('<<') and line.endswith('>>'):
                    return False
                return True

            def replace_tags(string, replacement=''):
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

            def pad_url(string):
                '''Pads urls to obtain a license'''
                if string.startswith('http'):
                    return f'\n    {string.strip()}\n'
                return string
            header = [h for h in header if filter_tags(h) and h]
            header = [replace_tags(h) for h in header]
            header = ['\n'.join(textwrap.wrap(h, 72)) + '\n' if len(h) > 72 else h for h in header]
            header = [pad_url(h) for h in header]

        print(f"-- {id}")
        license_folder.mkdir(parents=True, exist_ok=True)

        if not license_details_file.exists() or license_details_file.read_text() != detail_obj.text:
            license_details_file.write_text(detail_obj.text)

        license_text = detail['licenseText']
        license_text_file = license_folder / 'license.txt'
        if not license_text_file.exists() or license_text_file.read_text() != license_text:
            license_text_file.write_text(license_text)

        TEMPLATE_HEADER = '\n'.join(header)
        license_header_file.write_text(TEMPLATE_HEADER.strip() + '\n')

