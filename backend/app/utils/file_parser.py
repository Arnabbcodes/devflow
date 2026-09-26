import os
import json
import re
from pathlib import Path
from typing import Dict, Any, List

IGNORED_DIRS = {
    ".git", "__pycache__", ".venv", "venv", "env",
    "node_modules", ".idea", ".vscode", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", "build", "dist", ".dart_tool"
}

IGNORED_EXTENSIONS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg",
    ".zip", ".tar", ".gz", ".7z", ".pdf", ".pyc", ".pyo",
    ".exe", ".bin", ".dylib", ".so", ".dll", ".woff", ".woff2"
}

MAX_FILE_SIZE = 500 * 1024  # 500 KB per file


def parse_project_directory(directory_path: Path) -> Dict[str, Any]:
    """
    Scans a directory, extracts text files, and formats them into
    a unified project string for AI analysis.
    """
    directory_path = Path(directory_path).resolve()
    sections = []
    file_list = []

    for root, dirs, files in os.walk(directory_path):
        # Prune ignored directories in-place
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS and not d.startswith(".")]

        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(directory_path).as_posix()

            if file_path.suffix.lower() in IGNORED_EXTENSIONS:
                continue

            try:
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue

                content = file_path.read_text(encoding="utf-8", errors="replace")
                sections.append(f"===== {rel_path} =====\n{content}\n")
                file_list.append(rel_path)
            except Exception:
                # Skip unreadable or corrupted files
                continue

    combined_text = "\n".join(sections)
    return {
        "project_text": combined_text,
        "file_count": len(file_list),
        "files": file_list
    }


def parse_json_safely(raw_text: str) -> Dict[str, Any]:
    """
    Extracts and parses JSON from raw LLM output, stripping markdown code blocks
    or extracting the outermost JSON object if needed.
    """
    clean_text = raw_text.strip()

    # Strip markdown code blocks like ```json ... ```
    if clean_text.startswith("```"):
        clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text)
        clean_text = re.sub(r"\s*```$", "", clean_text)
        clean_text = clean_text.strip()

    try:
        return json.loads(clean_text)
    except json.JSONDecodeError:
        # Fallback: extract substring between first { and last }
        start = clean_text.find("{")
        end = clean_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            json_substr = clean_text[start : end + 1]
            return json.loads(json_substr)
        raise ValueError(f"Could not parse valid JSON from AI response: {raw_text[:200]}...")
