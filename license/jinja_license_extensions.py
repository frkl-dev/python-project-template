import json
from functools import lru_cache
from pathlib import Path
from typing import Set, Union, Dict, Any

import yaml
from jinja2 import nodes
from jinja2.ext import Extension

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
def available_licenses() -> Set[str]:
    """Get a list of available licenses."""

    template_root = get_template_root()
    print(template_root)
    licenses_dir = template_root / 'license' / 'license_data' / 'spdx_licenses'

    licenses: Set[str] = {
        path.stem
        for path in licenses_dir.iterdir() if path.is_dir()
    }
    print(licenses)
    return licenses

@lru_cache(maxsize=None)
def license_data(license_id: str) -> Dict[str, Any] | None:
    """Get the license text for a license identifier."""

    template_root = get_template_root()
    licenses_dir = template_root / 'license' / 'license_data' / 'spdx_licenses'

    license_file = licenses_dir / license_id / 'details.json'
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
    licenses_dir = template_root / 'license' / 'license_data' / 'spdx_licenses'

    license_file = licenses_dir / license_id / 'license.txt'

    if license_file.exists():
        text = license_file.read_text().strip()
        if text:
            return text
        else:
            return None
    else:
        return None

class LicenseTextExtension(Extension):
    """Jinja2 extension to map license identifiers to PyPI classifiers."""

    tags = {'license_text'}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        license_id = parser.parse_expression()
        args = [license_id]
        return nodes.Output([self.call_method('_lookup_text', args)]).set_lineno(lineno)

    def _lookup_text(self, license_id) -> str:
        """Lookup license text for a license identifier."""

        return license_text(license_id)

class LicenseListExtension(Extension):
    """Jinja2 extension to list all available licenses."""

    tags = {'license_list'}

    def parse(self, parser):
        lineno = next(parser.stream).lineno
        args = []
        return nodes.Output([self.call_method('_lookup_license_list', args)]).set_lineno(lineno)

    def _lookup_license_list(self):
        """Lookup PyPI classifier for a license identifier."""

        return sorted(available_licenses())