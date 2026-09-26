# DevFlow REST API Reference

Base URL: `http://127.0.0.1:8000`

Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`

---

## 1. System Endpoints

### `GET /`
Returns service metadata and readiness flags for Groq and Supabase.

#### Example Response:
```json
{
  "name": "DevFlow API",
  "version": "1.0.0",
  "status": "operational",
  "docs_url": "/docs",
  "groq_ready": true,
  "supabase_ready": false
}
```

---

### `GET /health`
Health check endpoint for container orchestrators and monitoring.

#### Example Response:
```json
{
  "status": "healthy",
  "groq_configured": true,
  "supabase_configured": false
}
```

---

## 2. Project Endpoints

### `POST /projects/upload`
Uploads a `.zip` project archive or creates a project record from source.

- **Content-Type**: `multipart/form-data`
- **Form Fields**:
  - `file`: (Optional) ZIP file of project
  - `name`: (Optional) Project name string
  - `description`: (Optional) Description string

#### Curl Example:
```bash
curl -X POST "http://127.0.0.1:8000/projects/upload" \
  -F "file=@demo-project.zip" \
  -F "name=demo-project" \
  -F "description=Evaluation Target"
```

#### Example Response:
```json
{
  "success": true,
  "message": "Project uploaded and indexed successfully.",
  "project": {
    "id": "e83b194a",
    "name": "demo-project",
    "description": "Evaluation Target",
    "status": "UPLOADED",
    "health_score": null,
    "file_count": 4,
    "created_at": "2026-09-26T00:00:00Z",
    "updated_at": "2026-09-26T00:00:00Z"
  }
}
```

---

### `GET /projects`
Retrieves all registered projects.

#### Example Response:
```json
{
  "success": true,
  "count": 3,
  "projects": [
    {
      "id": "demo-project-001",
      "name": "demo-project",
      "status": "READY",
      "health_score": 61,
      "file_count": 4
    }
  ]
}
```

---

### `GET /projects/{project_id}`
Retrieves detailed information for a specific project.

---

## 3. AI Analysis & Remediation Endpoints

### `POST /projects/{project_id}/analyze`
Initiates Groq AI multi-dimensional static analysis (Security, Bugs, Testing, Maintainability).

#### Example Response:
```json
{
  "summary": "DevFlow detected critical hardcoded credentials and unvalidated JWT tokens.",
  "health_score": 61,
  "issues": [
    {
      "id": "ISSUE-001",
      "title": "Hard-coded credentials & plain text authentication",
      "category": "Security",
      "severity": "CRITICAL",
      "file": "app.py",
      "line": 4,
      "description": "Hardcoded SECRET and plain-text admin credentials found in app.py.",
      "impact": "Complete unauthorized administrative access.",
      "recommendation": "Migrate secrets to environment variables."
    }
  ],
  "test_gaps": [
    "No negative tests for failed authentication"
  ],
  "strengths": [
    "Clean modular project layout"
  ]
}
```

---

### `POST /issues/fix`
Generates a safe fix plan, implementation steps, and code diff for a detected issue.

#### Request Body:
```json
{
  "issue_id": "ISSUE-001",
  "project_id": "demo-project-001"
}
```

#### Example Response:
```json
{
  "issue_id": "ISSUE-001",
  "root_cause": "Sensitive authentication tokens and credentials are hardcoded.",
  "files_to_change": ["app.py"],
  "implementation_steps": [
    "Extract SECRET into environment variable",
    "Enforce cryptographic signature validation"
  ],
  "regression_tests": [
    "test_auth_rejects_unverified_token"
  ],
  "code_diff": "@@ -39,6 +39,8 @@\n- return jwt.decode(token, options={\"verify_signature\": False})\n+ return jwt.decode(token, key=os.getenv(\"JWT_SECRET\"), algorithms=[\"HS256\"])"
}
```

---

### `POST /issues/tests`
Generates unit and regression tests for a detected issue.

#### Request Body:
```json
{
  "issue_id": "ISSUE-001"
}
```

#### Example Response:
```json
{
  "issue_id": "ISSUE-001",
  "test_cases": [
    {
      "name": "test_rejects_tampered_jwt_token",
      "purpose": "Verify tampered tokens return HTTP 401",
      "expected_result": "HTTP 401 Unauthorized",
      "test_code": "def test_rejects_tampered_jwt_token(client): ..."
    }
  ]
}
```

---

## 4. Verification & Release Gate Endpoints

### `POST /projects/{project_id}/verify`
Performs safe syntax verification using Python's native AST parser without code execution.

#### Example Response:
```json
{
  "passed": true,
  "total_files": 2,
  "passed_files": [
    "app.py",
    "tests/test_app.py"
  ],
  "failed_files": [],
  "details": "All Python files passed syntax verification."
}
```

---

### `POST /projects/{project_id}/report`
Compiles an executive release-readiness report combining issues and AST verification.

#### Example Response:
```json
{
  "project_id": "demo-project-001",
  "project_name": "demo-project",
  "release_ready": false,
  "health_score": 61,
  "summary": "Project has 2 high/critical issues requiring resolution.",
  "verification_status": "PASSED",
  "remaining_risks": [
    "Unprotected credentials in source code"
  ],
  "recommended_next_steps": [
    "Apply recommended Groq AI security patch",
    "Re-run verification gate"
  ]
}
```
