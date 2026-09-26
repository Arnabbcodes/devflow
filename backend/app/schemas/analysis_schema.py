from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone


def get_utc_now():
    return datetime.now(timezone.utc).isoformat()


class Issue(BaseModel):
    id: str
    title: str
    category: str  # "Security", "Bug", "Testing", "Maintainability"
    severity: str  # "CRITICAL", "HIGH", "MEDIUM", "LOW"
    file: str
    line: int
    description: str
    impact: str
    recommendation: str


class Analysis(BaseModel):
    summary: str
    health_score: int
    issues: List[Issue] = []
    test_gaps: List[str] = []
    strengths: List[str] = []
    created_at: str = Field(default_factory=get_utc_now)


class FixRequest(BaseModel):
    issue_id: str
    issue: Optional[Issue] = None
    project_id: Optional[str] = None
    code_context: Optional[str] = None


class FixPlan(BaseModel):
    issue_id: str
    root_cause: str
    files_to_change: List[str] = []
    implementation_steps: List[str] = []
    regression_tests: List[str] = []
    code_diff: Optional[str] = None


class TestRequest(BaseModel):
    issue_id: str
    issue: Optional[Issue] = None
    project_id: Optional[str] = None
    code_context: Optional[str] = None


class TestCase(BaseModel):
    name: str
    purpose: str
    expected_result: str
    test_code: Optional[str] = None


class TestPlan(BaseModel):
    issue_id: str
    test_cases: List[TestCase] = []


class VerificationResult(BaseModel):
    passed: bool
    total_files: int
    passed_files: List[str] = []
    failed_files: List[Dict[str, Any]] = []
    details: str = "Syntax verification completed."


class ReportResponse(BaseModel):
    project_id: str
    project_name: str
    release_ready: bool
    health_score: int
    summary: str
    detected_issues: List[Issue] = []
    verification_status: str
    remaining_risks: List[str] = []
    generated_at: str = Field(default_factory=get_utc_now)
