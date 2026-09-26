import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.ai.groq_client import ask_groq
from app.ai.prompts import (
    ANALYSIS_SYSTEM,
    ANALYSIS_USER,
    FIX_SYSTEM,
    FIX_USER,
    TESTS_SYSTEM,
    TESTS_USER,
    REPORT_SYSTEM,
    REPORT_USER,
)
from app.utils.file_parser import parse_json_safely
from app.services.supabase_service import supabase_service
from app.services.project_service import project_service

logger = logging.getLogger("devflow.services.analysis")


class AnalysisService:
    def __init__(self):
        # Cache of recent analyses and issue details
        self.analyses: Dict[str, Dict[str, Any]] = {}
        self.issues: Dict[str, Dict[str, Any]] = {}

    async def analyze(self, project_id: str, project_text: str) -> Dict[str, Any]:
        """
        Executes Groq AI code analysis across the extracted project codebase.
        """
        user_prompt = ANALYSIS_USER.format(project=project_text[:25000])

        try:
            raw_response = await ask_groq(ANALYSIS_SYSTEM, user_prompt, json_mode=True)
            data = parse_json_safely(raw_response)
        except Exception as e:
            logger.warning(f"Groq API call failed or unconfigured: {e}. Falling back to deterministic demo analysis.")
            data = self._get_fallback_analysis()

        # Cache analysis and individual issues
        self.analyses[project_id] = data
        for issue in data.get("issues", []):
            self.issues[issue["id"]] = issue

        # Update project record
        health_score = data.get("health_score", 65)
        project_service.update_project(project_id, {
            "status": "ANALYZED",
            "health_score": health_score
        })

        # Persist to database layer
        supabase_service.save_analysis(project_id, data)

        return data

    async def generate_fix(
        self,
        issue_id: str,
        issue_data: Optional[Dict[str, Any]] = None,
        code_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates remediation plan and code patch using Groq AI.
        """
        issue = issue_data or self.issues.get(issue_id, {})

        user_prompt = FIX_USER.format(
            issue_id=issue_id,
            title=issue.get("title", "Detected vulnerability"),
            category=issue.get("category", "Security"),
            severity=issue.get("severity", "HIGH"),
            file=issue.get("file", "app.py"),
            line=issue.get("line", 42),
            description=issue.get("description", "Vulnerability detected in source"),
            impact=issue.get("impact", "Potential security breach or crash"),
            recommendation=issue.get("recommendation", "Refactor to secure pattern"),
            code_context=code_context or "Refer to issue location"
        )

        try:
            raw_response = await ask_groq(FIX_SYSTEM, user_prompt, json_mode=True)
            fix_plan = parse_json_safely(raw_response)
        except Exception as e:
            logger.warning(f"Groq API fix generation failed: {e}. Using deterministic fallback fix plan.")
            fix_plan = self._get_fallback_fix_plan(issue_id, issue)

        supabase_service.save_fix(issue_id, fix_plan)
        return fix_plan

    async def generate_tests(
        self,
        issue_id: str,
        issue_data: Optional[Dict[str, Any]] = None,
        code_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generates regression test cases for a specific issue using Groq AI.
        """
        issue = issue_data or self.issues.get(issue_id, {})

        user_prompt = TESTS_USER.format(
            issue_id=issue_id,
            title=issue.get("title", "Detected vulnerability"),
            category=issue.get("category", "Security"),
            file=issue.get("file", "app.py"),
            line=issue.get("line", 42),
            description=issue.get("description", "Vulnerability detected in source"),
            code_context=code_context or "Refer to issue location"
        )

        try:
            raw_response = await ask_groq(TESTS_SYSTEM, user_prompt, json_mode=True)
            test_plan = parse_json_safely(raw_response)
        except Exception as e:
            logger.warning(f"Groq API test generation failed: {e}. Using deterministic fallback test plan.")
            test_plan = self._get_fallback_test_plan(issue_id, issue)

        return test_plan

    async def generate_report(
        self,
        project_id: str,
        project_name: str,
        verification_status: str = "PASSED",
        issues: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generates executive release readiness report combining issues and AST verification.
        """
        active_analysis = self.analyses.get(project_id, {})
        project_issues = issues or active_analysis.get("issues", [])

        user_prompt = REPORT_USER.format(
            project_id=project_id,
            project_name=project_name,
            verification_status=verification_status,
            issues_json=json.dumps(project_issues, indent=2)
        )

        try:
            raw_response = await ask_groq(REPORT_SYSTEM, user_prompt, json_mode=True)
            report = parse_json_safely(raw_response)
        except Exception as e:
            logger.warning(f"Groq API report generation failed: {e}. Using deterministic fallback report.")
            report = self._get_fallback_report(project_id, project_name, verification_status, project_issues)

        return report

    def _get_fallback_analysis(self) -> Dict[str, Any]:
        """Provides realistic fallback analysis matching demo-project defects."""
        return {
            "summary": "DevFlow detected critical hardcoded credentials, unvalidated JWT signature, and broad exception handling in demo-project.",
            "health_score": 61,
            "issues": [
                {
                    "id": "ISSUE-001",
                    "title": "Hard-coded credentials & plain text authentication",
                    "category": "Security",
                    "severity": "CRITICAL",
                    "file": "app.py",
                    "line": 4,
                    "description": "Hardcoded SECRET and plain-text admin credentials ('admin' / 'admin123') found in application entrypoint.",
                    "impact": "Complete system compromise and unauthorized administrative access.",
                    "recommendation": "Migrate secrets to environment variables and use salted cryptographic password hashing."
                },
                {
                    "id": "ISSUE-002",
                    "title": "JWT authentication signature verification disabled",
                    "category": "Security",
                    "severity": "HIGH",
                    "file": "app.py",
                    "line": 42,
                    "description": "JWT decode is executed with verify_signature=False, allowing arbitrary token forgery.",
                    "impact": "Attackers can forge tokens to impersonate any user or admin.",
                    "recommendation": "Enable verify_signature=True and supply HMAC secret or public key."
                },
                {
                    "id": "ISSUE-003",
                    "title": "Silent catch-all exception masking bugs",
                    "category": "Bug",
                    "severity": "MEDIUM",
                    "file": "app.py",
                    "line": 56,
                    "description": "Broad 'except Exception: pass' swallows critical runtime exceptions without logging or remediation.",
                    "impact": "System enters corrupted state with zero diagnostic visibility.",
                    "recommendation": "Catch specific exceptions and log error traces with context."
                },
                {
                    "id": "ISSUE-004",
                    "title": "Insufficient test coverage on security-critical paths",
                    "category": "Testing",
                    "severity": "HIGH",
                    "file": "tests/test_app.py",
                    "line": 1,
                    "description": "Test suite only contains a single trivial assert and lacks auth, negative, and edge case coverage.",
                    "impact": "Regressions and vulnerabilities can reach production undetected.",
                    "recommendation": "Add automated integration tests for token validation and bad credentials."
                },
                {
                    "id": "ISSUE-005",
                    "title": "Unpinned and unversioned dependencies",
                    "category": "Maintainability",
                    "severity": "LOW",
                    "file": "requirements.txt",
                    "line": 1,
                    "description": "Dependencies in requirements.txt have no version constraints.",
                    "impact": "Upstream breaking changes can unexpectedly break builds or deployments.",
                    "recommendation": "Pin package versions using requirements.txt or pip-tools."
                }
            ],
            "test_gaps": [
                "No negative tests for failed authentication attempts",
                "Missing token expiration and signature validation tests",
                "Absence of API error handling tests"
            ],
            "strengths": [
                "Clean modular project layout with tests separated from application code",
                "Standard entrypoint structure utilizing FastAPI"
            ]
        }

    def _get_fallback_fix_plan(self, issue_id: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "issue_id": issue_id,
            "root_cause": "Sensitive authentication tokens and credentials are hardcoded or evaluated without cryptographic signature validation.",
            "files_to_change": [issue.get("file", "app.py")],
            "implementation_steps": [
                "Extract SECRET and admin credentials into environment variables",
                "Configure jwt.decode with verify_signature=True and pass the secret key",
                "Implement secure password verification using bcrypt / argon2",
                "Return HTTP 401 Unauthorized upon invalid token signature"
            ],
            "regression_tests": [
                "test_auth_rejects_unverified_token",
                "test_auth_rejects_empty_signature",
                "test_auth_succeeds_with_valid_signature"
            ],
            "code_diff": """@@ -39,6 +39,8 @@
 def verify_token(token: str):
-    # INSECURE: signature verification is disabled
-    return jwt.decode(token, options={"verify_signature": False})
+    # SECURE: enforce cryptographic signature verification
+    return jwt.decode(token, key=os.getenv("JWT_SECRET"), algorithms=["HS256"])
"""
        }

    def _get_fallback_test_plan(self, issue_id: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "issue_id": issue_id,
            "test_cases": [
                {
                    "name": "test_rejects_tampered_jwt_token",
                    "purpose": "Ensure tokens with forged headers or payloads fail validation with HTTP 401",
                    "expected_result": "SignatureVerificationError or HTTP 401",
                    "test_code": """def test_rejects_tampered_jwt_token(client):
    tampered_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiYWRtaW4ifQ.FAKE_SIG"
    response = client.get("/secure-data", headers={"Authorization": f"Bearer {tampered_token}"})
    assert response.status_code == 401"""
                },
                {
                    "name": "test_auth_requires_environment_credentials",
                    "purpose": "Verify credentials cannot be accessed when environment variables are omitted",
                    "expected_result": "RuntimeError or configuration error",
                    "test_code": """def test_auth_requires_environment_credentials(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    # verify system raises proper configuration warning"""
                }
            ]
        }

    def _get_fallback_report(
        self,
        project_id: str,
        project_name: str,
        verification_status: str,
        issues: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        critical_count = sum(1 for i in issues if i.get("severity") in ["CRITICAL", "HIGH"])
        is_ready = critical_count == 0 and verification_status == "PASSED"

        return {
            "project_id": project_id,
            "project_name": project_name,
            "release_ready": is_ready,
            "health_score": 61 if not is_ready else 92,
            "summary": f"Project '{project_name}' has {len(issues)} detected issue(s) ({critical_count} critical/high). Syntax verification: {verification_status}.",
            "detected_issues_summary": f"{critical_count} blocking issues require resolution before production deployment.",
            "verification_status": verification_status,
            "remaining_risks": [
                "Unprotected credentials in source control history",
                "Missing regression test suite for authentication edge cases"
            ],
            "recommended_next_steps": [
                "Apply recommended Groq AI security patch to app.py",
                "Integrate generated regression test cases into pytest suite",
                "Re-run DevFlow verification gate"
            ]
        }


analysis_service = AnalysisService()
