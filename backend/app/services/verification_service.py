import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Union


class VerificationService:
    """
    Validates Python syntax across codebase using standard Python AST parsing.
    Ensures safe code verification without executing arbitrary code.
    """

    def verify_source_string(self, source_code: str, filename: str = "snippet.py") -> Dict[str, Any]:
        """Verifies syntax of an in-memory python source string."""
        try:
            ast.parse(source_code, filename=filename)
            return {
                "file": filename,
                "passed": True,
                "error": None,
                "line": None
            }
        except SyntaxError as error:
            return {
                "file": filename,
                "passed": False,
                "error": str(error),
                "line": error.lineno
            }

    def verify_file(self, file_path: Union[Path, str]) -> Dict[str, Any]:
        """Reads and verifies syntax of a specific file on disk."""
        path = Path(file_path)
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
            return self.verify_source_string(source, filename=path.name)
        except Exception as e:
            return {
                "file": path.name,
                "passed": False,
                "error": f"Failed to read file: {str(e)}",
                "line": None
            }

    def verify_project_directory(self, directory_path: Union[Path, str]) -> Dict[str, Any]:
        """
        Scans all .py files in a project directory and validates each with AST.
        """
        dir_path = Path(directory_path).resolve()
        py_files = list(dir_path.rglob("*.py"))

        passed_files: List[str] = []
        failed_files: List[Dict[str, Any]] = []

        for f in py_files:
            # Skip virtual environments and hidden files
            rel_parts = f.relative_to(dir_path).parts
            if any(part in {"venv", ".venv", "env", "__pycache__", ".git"} for part in rel_parts):
                continue

            rel_name = f.relative_to(dir_path).as_posix()
            res = self.verify_file(f)
            if res["passed"]:
                passed_files.append(rel_name)
            else:
                failed_files.append({
                    "file": rel_name,
                    "error": res["error"],
                    "line": res["line"]
                })

        all_passed = len(failed_files) == 0
        total = len(passed_files) + len(failed_files)

        return {
            "passed": all_passed,
            "total_files": total,
            "passed_files": passed_files,
            "failed_files": failed_files,
            "details": "All Python files passed syntax verification." if all_passed else f"{len(failed_files)} file(s) failed syntax verification."
        }

    def verify_project_text(self, project_text: str) -> Dict[str, Any]:
        """
        Extracts sections formatted like '===== filename.py =====' from project text
        and checks syntax for each python file section.
        """
        pattern = r"=====\s*([^\s=]+\.py)\s*=====\n(.*?)(?=(?:=====\s*[^\s=]+\s*=====|\Z))"
        matches = re.findall(pattern, project_text, flags=re.DOTALL)

        passed_files: List[str] = []
        failed_files: List[Dict[str, Any]] = []

        for filename, content in matches:
            res = self.verify_source_string(content, filename=filename)
            if res["passed"]:
                passed_files.append(filename)
            else:
                failed_files.append({
                    "file": filename,
                    "error": res["error"],
                    "line": res["line"]
                })

        total = len(passed_files) + len(failed_files)
        all_passed = len(failed_files) == 0

        return {
            "passed": all_passed,
            "total_files": total,
            "passed_files": passed_files,
            "failed_files": failed_files,
            "details": "All extracted Python modules passed AST syntax verification." if all_passed else f"{len(failed_files)} module(s) have syntax errors."
        }


verification_service = VerificationService()
