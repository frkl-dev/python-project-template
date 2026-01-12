import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Set, Union

import yaml
from jinja2 import nodes
from jinja2.ext import Extension

DEFAULT_LICENSES = [
    "PolyForm-Noncommercial-1.0.0",
    "MIT",
    "Apache-2.0",
    "GPL-2.0-only",
    "GPL-3.0-only",
    "LGPL-2.1-only",
    "BSD-3-Clause",
    "BSD-2-Clause",
    "GPL-2.0-or-later",
    "LGPL-3.0-only",
    "BSD-0-Clause",
    "ISC",
    "CC0-1.0",
    "Unlicense",
    "GPL-3.0-or-later",
    "MPL-2.0",
    "LGPL-2.0-only",
    "AGPL-3.0-only",
    "Artistic-2.0",
    "EPL-2.0",
    "0BSD",
]


def get_template_root():
    """Get the template root directory."""
    # This will find the template root by looking for copier.yml
    current = Path(__file__).parent

    while current != current.parent:
        if (current / "copier.yml").exists():
            return current
        current = current.parent
    # Fallback to the directory containing this file
    return Path(__file__).parent


@lru_cache(maxsize=None)
def available_licenses(display_all: bool = False) -> Set[str]:
    """Get a list of available licenses."""

    template_root = get_template_root()
    licenses_dir = template_root / "license" / "license_data" / "spdx_licenses"

    licenses: Set[str] = {
        path.name
        for path in licenses_dir.iterdir()
        if path.is_dir() and (display_all or path.name in DEFAULT_LICENSES)
    }
    return licenses


@lru_cache(maxsize=None)
def license_data(license_id: str) -> Dict[str, Any] | None:
    """Get the license text for a license identifier."""

    template_root = get_template_root()
    licenses_dir = template_root / "license" / "license_data" / "spdx_licenses"

    license_file = licenses_dir / license_id / "details.json"
    if license_file.exists():
        text = license_file.read_text()
        data = json.loads(text)
        if not isinstance(data, dict):
            raise ValueError(f"Invalid license data for {license_id}: not a dictionary")
        return data
    else:
        return None


@lru_cache(maxsize=None)
def license_text(license_id: str) -> str | None:
    """Get the license text for a license identifier."""

    template_root = get_template_root()
    licenses_dir = template_root / "license" / "license_data" / "spdx_licenses"

    license_file = licenses_dir / license_id / "license.txt"

    if license_file.exists():
        text = license_file.read_text().strip()
        if text:
            return text
        else:
            return None
    else:
        return None


def license_header(license_ids: List[str]) -> str | None:
    """Get the license header for one or multiple license identifiers."""

    template_root = get_template_root()
    licenses_dir = template_root / "license" / "license_data" / "spdx_licenses"

    all_headers = {}
    for license_id in license_ids:
        license_file = licenses_dir / license_id / "header.txt"

        if license_file.exists():
            text = license_file.read_text().strip()
            if text:
                all_headers[license_id] = text
            else:
                raise Exception(f"License header for license not found: {license_id}")

        else:
            raise Exception(f"License id not found: {license_id}")

    spdx_expr = " OR ".join(license_ids)

    spdx_header = f"SPDX-License-Identifier: {spdx_expr}"

    if len(license_ids) == 1:
        msg = all_headers[license_ids[0]]
    else:
        msg = "This file is licensed under multiple licenses:\n\n"

        for license_id, header in all_headers.items():
            msg += f"- {license_id}:\n{header}\n\n"

    result = f"{spdx_header}\n\n{msg}".strip()
    return json.dumps(result)[1:-1]


class LicenseTextExtension(Extension):
    """Jinja2 extension to map license identifiers to PyPI classifiers."""

    tags = {"license_text"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        license_id = parser.parse_expression()
        args = [license_id]
        return nodes.Output([self.call_method("_lookup_text", args)]).set_lineno(lineno)

    def _lookup_text(self, license_id) -> str:
        """Lookup license text for a license identifier."""

        return license_text(license_id)


class LicenseListExtension(Extension):
    """Jinja2 extension to list all available licenses."""

    tags = {"license_list"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno

        # Check if there are any arguments
        if parser.stream.current.test("block_end"):
            # No arguments provided, use default
            display_all = nodes.Const(False)
        else:
            # Parse the display_all argument
            display_all = parser.parse_expression()

        args = [display_all]
        return nodes.Output(
            [self.call_method("_lookup_license_list", args)]
        ).set_lineno(lineno)

    def _lookup_license_list(self, display_all: bool = False):
        """Lookup PyPI classifier for a license identifier."""

        display_all = False
        return sorted(available_licenses(display_all=display_all))


class LicenseHeaderExtension(Extension):
    """Jinja2 extension to map license identifiers to PyPI classifiers."""

    tags = {"license_header"}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        license_ids = parser.parse_expression()
        args = [license_ids]
        return nodes.Output([self.call_method("_lookup_header", args)]).set_lineno(
            lineno
        )

    def _lookup_header(self, license_ids) -> str:
        """Lookup license text for a license identifier."""

        return license_header(license_ids)
