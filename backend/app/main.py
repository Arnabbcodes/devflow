import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import (
    CORS_ORIGINS,
    GROQ_API_KEY,
    SUPABASE_URL,
    SUPABASE_KEY,
)
from app.schemas.project_schema import (
    Project,
    ProjectResponse,
    ProjectListResponse,
)
from app.schemas.analysis_schema import (
    Analysis,
    FixRequest,
    FixPlan,
    TestRequest,
    TestPlan,
    VerificationResult,
    ReportResponse,
)
from app.services.project_service import project_service
from app.services.analysis_service import analysis_service
from app.services.verification_service import verification_service
from app.services.supabase_service import supabase_service
from app.utils.zip_handler import extract_zip_safely
from app.utils.file_parser import parse_project_directory

app = FastAPI(
    title="DevFlow API",
    description="DevFlow Backend: AI-Powered Code Quality, Security Analysis & AST Verification Engine",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["System"])
def root():
    return {
        "name": "DevFlow API",
        "version": "1.0.0",
        "status": "operational",
        "docs_url": "/docs",
        "groq_ready": bool(GROQ_API_KEY and GROQ_API_KEY != "YOUR_GROQ_API_KEY"),
        "supabase_ready": supabase_service.is_enabled,
    }


@app.get("/health", tags=["System"])
def health():
    return {
        "status": "healthy",
        "groq_configured": bool(GROQ_API_KEY and GROQ_API_KEY != "YOUR_GROQ_API_KEY"),
        "supabase_configured": supabase_service.is_enabled,
    }


# -------------------------------------------------------------------
# PROJECTS ENDPOINTS
# -------------------------------------------------------------------

@app.post("/projects/upload", response_model=ProjectResponse, tags=["Projects"])
async def upload_project(
    file: Optional[UploadFile] = File(None),
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(""),
):
    """
    Uploads a project archive (ZIP) or initializes a project with sample code.
    Extracts files safely, indexes text content, and creates a project record.
    """
    project_name = name or (file.filename.rsplit(".", 1)[0] if file else "uploaded-project")
    project_text = ""
    file_count = 0
    extracted_dir = None

    if file:
        if not file.filename.endswith(".zip"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only .zip project archives are supported."
            )

        content = await file.read()
        temp_dir = Path(tempfile.mkdtemp(prefix="devflow_"))
        try:
            extracted_path = extract_zip_safely(content, temp_dir)
            parsed_data = parse_project_directory(extracted_path)
            project_text = parsed_data["project_text"]
            file_count = parsed_data["file_count"]
            extracted_dir = str(extracted_path)
        except Exception as e:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to process project archive: {str(e)}"
            )

    # If no file uploaded, check if demo-project exists locally as default context
    if not project_text:
        demo_dir = Path(__file__).resolve().parent.parent.parent / "demo-project"
        if demo_dir.exists():
            parsed_data = parse_project_directory(demo_dir)
            project_text = parsed_data["project_text"]
            file_count = parsed_data["file_count"]
            extracted_dir = str(demo_dir)

    record = project_service.create_project(
        name=project_name,
        project_text=project_text,
        description=description or "",
        file_count=file_count,
        directory_path=extracted_dir,
    )

    return ProjectResponse(
        success=True,
        message="Project uploaded and indexed successfully.",
        project=Project(**record),
    )


@app.get("/projects", response_model=ProjectListResponse, tags=["Projects"])
def list_projects():
    """Lists all registered projects."""
    projects = project_service.list_projects()
    return ProjectListResponse(
        success=True,
        count=len(projects),
        projects=[Project(**p) for p in projects],
    )


@app.get("/projects/{project_id}", response_model=Project, tags=["Projects"])
def get_project(project_id: str):
    """Retrieves a specific project by ID."""
    proj = project_service.get_project(project_id)
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )
    return Project(**proj)


# -------------------------------------------------------------------
# AI ANALYSIS ENDPOINTS
# -------------------------------------------------------------------

@app.post("/projects/{project_id}/analyze", response_model=Analysis, tags=["Analysis"])
async def analyze_project(project_id: str):
    """
    Triggers Groq AI code analysis for the project codebase.
    Returns detected security vulnerabilities, bugs, test gaps, and health score.
    """
    proj = project_service.get_project(project_id)
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    project_text = proj.get("project_text")
    if not project_text:
        # Check if project has a directory to re-parse or use demo-project
        if proj.get("directory_path") and Path(proj["directory_path"]).exists():
            parsed = parse_project_directory(Path(proj["directory_path"]))
            project_text = parsed["project_text"]
        else:
            demo_dir = Path(__file__).resolve().parent.parent.parent / "demo-project"
            if demo_dir.exists():
                parsed = parse_project_directory(demo_dir)
                project_text = parsed["project_text"]
            else:
                project_text = "===== app.py =====\n# Empty project source\n"

    result = await analysis_service.analyze(project_id, project_text)
    return Analysis(**result)


@app.post("/issues/fix", response_model=FixPlan, tags=["Remediation"])
async def generate_fix(req: FixRequest):
    """
    Generates a safe remediation plan and code patch for a detected issue.
    """
    fix_plan = await analysis_service.generate_fix(
        issue_id=req.issue_id,
        issue_data=req.issue.model_dump() if req.issue else None,
        code_context=req.code_context,
    )
    return FixPlan(**fix_plan)


@app.post("/issues/tests", response_model=TestPlan, tags=["Remediation"])
async def generate_tests(req: TestRequest):
    """
    Generates regression and unit tests for a detected issue using Groq AI.
    """
    test_plan = await analysis_service.generate_tests(
        issue_id=req.issue_id,
        issue_data=req.issue.model_dump() if req.issue else None,
        code_context=req.code_context,
    )
    return TestPlan(**test_plan)


# -------------------------------------------------------------------
# VERIFICATION & REPORT ENDPOINTS
# -------------------------------------------------------------------

@app.post("/projects/{project_id}/verify", response_model=VerificationResult, tags=["Verification"])
def verify_project(project_id: str):
    """
    Performs Python AST syntax verification without executing arbitrary code.
    Validates that all Python files parse into valid syntax trees.
    """
    proj = project_service.get_project(project_id)
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    # 1. Verify directory if available
    dir_path = proj.get("directory_path")
    if dir_path and Path(dir_path).exists():
        verification = verification_service.verify_project_directory(dir_path)
    # 2. Or verify extracted project_text
    elif proj.get("project_text"):
        verification = verification_service.verify_project_text(proj["project_text"])
    else:
        # Fallback to local demo-project directory
        demo_dir = Path(__file__).resolve().parent.parent.parent / "demo-project"
        if demo_dir.exists():
            verification = verification_service.verify_project_directory(demo_dir)
        else:
            verification = {
                "passed": True,
                "total_files": 0,
                "passed_files": [],
                "failed_files": [],
                "details": "No Python files found to verify."
            }

    supabase_service.save_verification(project_id, verification)
    return VerificationResult(**verification)


@app.post("/projects/{project_id}/report", response_model=ReportResponse, tags=["Release Report"])
async def generate_release_report(project_id: str):
    """
    Compiles an executive release-readiness report evaluating detected issues,
    AST verification results, and outstanding risks.
    """
    proj = project_service.get_project(project_id)
    if not proj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project '{project_id}' not found."
        )

    # Run verification to get active verification status
    v_res = verify_project(project_id)
    verification_status = "PASSED" if v_res.passed else "FAILED"

    report = await analysis_service.generate_report(
        project_id=project_id,
        project_name=proj.get("name", "Project"),
        verification_status=verification_status,
    )
    return ReportResponse(**report)
