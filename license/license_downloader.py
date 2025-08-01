#!/usr/bin/env python3
"""
License Downloader

A helper to download license texts from SPDX.org based on license identifiers.
"""

import os
import sys
import urllib.request
import urllib.error
from typing import List
from pathlib import Path


def download_licenses(license_ids: List[str], target_dir: str, overwrite: bool = False) -> None:
    """
    Download license texts from SPDX.org and save them to the target directory.
    
    Args:
        license_ids: A list of license identifiers (e.g., 'MIT', 'BSD-2-Clause')
        target_dir: The directory where license files will be saved
    
    Returns:
        None
    
    Raises:
        ValueError: If license_ids is empty or contains invalid identifiers
        IOError: If target_dir cannot be created or written to
        requests.RequestException: If there's an error downloading the license text
    """
    if not license_ids:
        raise ValueError("License IDs list cannot be empty")
    
    # Create target directory if it doesn't exist
    target_path = Path(target_dir)

    try:
        target_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise IOError(f"Failed to create target directory: {e}")
    
    # Base URL for SPDX license texts
    base_url = "https://spdx.org/licenses/{}.txt"
    
    for license_id in license_ids:
        # Construct the URL for the license
        license_url = base_url.format(license_id)
        
        # Construct the output file path
        output_file = target_path / f"{license_id}.txt"

        if output_file.exists() and not overwrite:
            print(f"License file {output_file} already exists. Skipping.")
            continue
        
        try:
            # Download the license text
            with urllib.request.urlopen(license_url) as response:
                license_text = response.read().decode('utf-8')

            # replcae possible windows line endings
            license_text = license_text.replace("\r\n", "\n")
            
            # Write the license text to a file
            with open(output_file, 'w') as f:
                f.write(license_text)
            
            print(f"Successfully downloaded license '{license_id}' to {output_file}")
            
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            print(f"Error downloading license '{license_id}': {e}")
            # Continue with the next license instead of stopping completely
    
    print(f"License download complete. Files saved to {target_dir}. Make sure to check the license files for placeholders and replace them with the appropriate jinja variables.")


if __name__ == "__main__":

    target_dir = sys.argv[1]
    licenses = sys.argv[2:]

    download_licenses(license_ids=licenses, target_dir=target_dir)