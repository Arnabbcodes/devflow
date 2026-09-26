import os
import zipfile
import io
import shutil
from pathlib import Path
from typing import Union


def extract_zip_safely(zip_source: Union[bytes, io.BytesIO, Path, str], extract_to: Union[Path, str]) -> Path:
    """
    Safely extracts a ZIP archive into the destination directory.
    Guards against Zip Slip (directory traversal) vulnerabilities.
    """
    extract_path = Path(extract_to).resolve()
    extract_path.mkdir(parents=True, exist_ok=True)

    if isinstance(zip_source, bytes):
        zip_file = zipfile.ZipFile(io.BytesIO(zip_source))
    elif isinstance(zip_source, (Path, str)):
        zip_file = zipfile.ZipFile(zip_source)
    else:
        zip_file = zipfile.ZipFile(zip_source)

    try:
        for member in zip_file.infolist():
            # Normalize member path
            filename = member.filename
            
            # Skip entries with malicious relative paths
            if filename.startswith("/") or filename.startswith("\\") or ".." in filename:
                raise ValueError(f"Unsafe path detected in ZIP member: {filename}")

            target_file_path = (extract_path / filename).resolve()

            # Verify target path is strictly within extract_path
            try:
                target_file_path.relative_to(extract_path)
            except ValueError:
                raise ValueError(f"Zip slip path traversal attempt blocked: {filename}")

            if member.is_dir():
                target_file_path.mkdir(parents=True, exist_ok=True)
            else:
                target_file_path.parent.mkdir(parents=True, exist_ok=True)
                with zip_file.open(member) as source, open(target_file_path, "wb") as dest:
                    shutil.copyfileobj(source, dest)

        return extract_path
    finally:
        zip_file.close()
