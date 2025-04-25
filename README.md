
# PYPI Package Scraper

## Overview

The PYPI Package Scraper is a Python tool that fetches the latest version of a specified Python package from the Python Package Index (PYPI), downloads the corresponding package file, and extracts its dependencies.

## Features

- Retrieves the latest version of a package from PYPI.
- Downloads the package file in formats like `.whl`, `.tar.gz`, or `.zip`.
- Extracts dependencies from metadata files (`setup.py`, `requirements.txt`, `METADATA`).

## Requirements

- Python 3.x
- `requests` library: Install with `pip install requests`

## Usage

1. Clone or download the repository.
2. Install required packages: 
   ```
   pip install requests
   ```
3. Run the script:
   ```
   python scraper.py
   ```
4. Enter the package name when prompted (e.g., `requests`).

The script fetches metadata, displays the latest version, downloads the package, and lists dependencies.

### Example Output:
```
Enter package name: requests
Latest version of 'requests': 2.28.1
Dependencies:
 - chardet
 - idna
 - urllib3
 - certifi
Structured List:
{
    'package': 'requests',
    'version': '2.28.1',
    'dependencies': ['chardet', 'idna', 'urllib3', 'certifi']
}
```

## How It Works

1. Fetches package metadata from the PYPI JSON API.
2. Downloads a compatible file (`.whl`, `.tar.gz`, `.zip`).
3. Extracts dependencies from the package’s metadata.