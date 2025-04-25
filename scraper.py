import os
import requests
import zipfile
import tarfile
from typing import Tuple

#fetches package metadata from the pypi json api
def fetch_package_data(package_name: str) -> dict | None:
    try:
        response = requests.get(
            f"https://pypi.org/pypi/{package_name}/json", timeout=10
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError, KeyError) as e:
        print(f"Error fetching package data: {e}")
        return None


#locates a valid downloadable url for a file (.whl, .tar.gz, or .zip)
def find_download_url(package_data: dict, version: str) -> tuple[str | None, str | None]:
    for extension in [".whl", ".tar.gz", ".zip"]:
        for file_info in package_data.get("releases", {}).get(version, []):
            if file_info["filename"].endswith(extension):
                return file_info["url"], file_info["filename"]
    print("No valid distribution file found.")
    return None, None


#downloads the release file from pypi and saves it locally
def download_file(url: str, filename: str, folder: str = "downloads") -> str | None:
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)

    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return path
    except requests.RequestException as e:
        print(f"Download failed: {e}")
        return None


#chooses the right extraction method based on the file type
def extract_dependencies(path: str) -> list[str]:
    if path.endswith((".whl", ".zip")):
        return extract_from_zip(path)
    elif path.endswith(".tar.gz"):
        return extract_from_tar(path)
    return []


#extracts dependencies from a whl or zip file (using METADATA)
def extract_from_zip(path: str) -> list[str]:
    with zipfile.ZipFile(path) as zipf:
        for name in zipf.namelist():
            if name.endswith("METADATA"):
                with zipf.open(name) as f:
                    return extract_from_metadata(f)
    return []


#parses dependency lines from a METADATA file
def extract_from_metadata(file: zipfile.ZipExtFile):
    dependencies = []
    for line in file.read().decode().splitlines():
        if line.startswith("Requires-Dist:"):
            dependencies.append(line.replace("Requires-Dist:", "").strip())
    return dependencies


#extracts dependencies from a tar.gz archive (requirements.txt and setup.py)
def extract_from_tar(path: str) -> list[str]:
    dependencies = []
    found_setup = False

    try:
        with tarfile.open(path, "r:gz") as tar:
            for member in tar.getmembers():
                if member.name.endswith("setup.py"):
                    found_setup = True

                if member.name.endswith("requirements.txt"):
                    requirements_file = tar.extractfile(member)
                    if requirements_file:
                        dependencies.extend(
                            line.decode().strip()
                            for line in requirements_file
                            if line.strip() and not line.startswith(b"#")
                        )
    except (tarfile.TarError, IOError) as e:
        print(f"Error reading tar.gz file: {e}")
        return []

    if not found_setup:
        print("Warning: setup.py not found in the archive.")

    return dependencies


#prints metadata like version, summary, and author info
def display_metadata(data: dict, name: str) -> str:
    version = data["info"]["version"]
    print(f"Latest version of '{name}': {version}")
    print(f"Summary: {data['info'].get('summary', 'No summary')}")
    print(f"Author: {data['info'].get('author', 'Unknown')}")
    return version


#main execution function: gets user input, fetches, downloads, and extracts dependencies
def main():
    package = input("Enter package name: ").strip().lower()
    data = fetch_package_data(package)
    if not data:
        print("Failed to fetch package data.")
        return

    version = display_metadata(data, package)
    url, filename = find_download_url(data, version)
    if not url:
        return

    path = download_file(url, filename)
    if not path:
        return

    deps = extract_dependencies(path)
    if deps:
        print("Dependencies:")
        for d in deps:
            print(f" - {d}")
    else:
        print("No dependencies found.")

    return {
        "package": package,
        "version": version,
        "dependencies": deps
    }



if __name__ == "__main__":
    result = main()
    if result:
        print("\nStructured List:")
        print(result)
