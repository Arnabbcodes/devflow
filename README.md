# DevFlow ⚡

> **AI-Powered Code Review, Security Auditing & Release Gatekeeper**

DevFlow is an autonomous software quality and release-readiness engine designed to bridge the gap between rapid software development and rigorous production safety. By coupling **Groq AI (llama-3.3-70b-versatile)** with safe **Python AST static syntax verification**, DevFlow analyzes codebases, detects security flaws and regressions, synthesizes surgical code fixes, and enforces automated release gating without running untrusted code.

---

## 🌟 Key Features

- 🛡️ **Multi-Vector AI Auditing**: Detects security vulnerabilities (OWASP top 10, credential leaks, unverified JWTs), logic bugs, test coverage gaps, and maintainability antipatterns.
- ⚡ **Sub-Second Remediation**: Generates step-by-step root-cause analyses, implementation roadmaps, unified code diffs, and regression test suites.
- 🔒 **Zero Remote Code Execution (Zero RCE)**: Uses Python's native AST parser (`ast.parse`) for strict syntax verification without executing untrusted user code.
- 🗂️ **Zip Slip Protected**: Hardened upload pipeline preventing path traversal exploits from uploaded `.zip` archives.
- 📊 **Executive Release Gatekeeper**: Combines syntax verification with defect severity metrics to render a clear Go/No-Go release decision.
- ☁️ **Cloud Native & Offline Resilient**: Connects to **Supabase PostgreSQL** with Row-Level Security (RLS) while providing automated local in-memory fallback.

---

## 🛠️ Technology Stack & Separation of Roles

| Technology | Role | Details |
| :--- | :--- | :--- |
| **Flutter (Dart)** | **Frontend Dashboard** | Material 3 dark interface with live charts (`fl_chart`), audit flows, and remediation views. |
| **FastAPI (Python)** | **Backend API Server** | Asynchronous REST API, multipart ZIP handling, CORS orchestration, and Pydantic validation. |
| **Groq (`llama-3.3-70b`)** | **Runtime Application AI** | High-throughput LLM runtime powering live code analysis, fix generation, and test synthesis. |
| **Python AST (`ast.parse`)** | **Verification Engine** | Fast, deterministic, and safe syntax verification ensuring zero execution side-effects. |
| **Supabase (PostgreSQL)** | **Cloud Persistence** | Normalized relational schema with Row-Level Security (RLS) policies for user data isolation. |
| **IBM Bob 2.0** | **AI Engineering Copilot** | Autonomous development partner utilized across architecture, implementation, debugging, and documentation. |

> 💡 **Architectural Clarification**: Groq powers DevFlow's runtime AI features within the product, while IBM Bob 2.0 was used as an AI-assisted software engineering copilot throughout the development lifecycle.

---

## 📂 Project Structure

```text
devflow/
├── frontend/                    # Flutter cross-platform user interface
│   ├── lib/
│   │   ├── main.dart            # Flutter application entrypoint & screens
│   │   ├── models/              # Client-side data models
│   │   └── widgets/             # UI components
│   └── pubspec.yaml
│
├── backend/                     # FastAPI asynchronous backend service
│   ├── .env                     # Local environment credentials (ignored by git)
│   ├── .env.example             # Template environment variables
│   ├── requirements.txt         # Python dependencies
│   └── app/
│       ├── main.py              # Main API router and endpoints
│       ├── config/
│       │   └── settings.py      # Environment configuration reader
│       ├── ai/
│       │   ├── groq_client.py   # Async Groq client with JSON enforcement
│       │   └── prompts.py       # Production prompt engineering definitions
│       ├── services/
│       │   ├── project_service.py      # Project lifecycle management
│       │   ├── analysis_service.py     # AI analysis & remediation engine
│       │   ├── verification_service.py # Python AST syntax verifier
│       │   └── supabase_service.py     # Supabase database & fallback layer
│       ├── utils/
│       │   ├── file_parser.py   # Directory walker & unified code extractor
│       │   └── zip_handler.py   # Zip Slip safe extraction engine
│       └── schemas/
│           ├── project_schema.py       # Pydantic models for projects
│           └── analysis_schema.py      # Pydantic models for issues & fixes
│
├── supabase/                    # Database schemas and security rules
│   ├── 001_initial_schema.sql   # Relational tables, indexes, and constraints
│   └── 002_rls_policies.sql     # Row-Level Security policies
│
├── demo-project/                # Intentional flaw testbed for live judging
│   ├── README.md
│   ├── requirements.txt
│   ├── app.py                   # Hardcoded secrets, unverified JWT, broad except
│   └── tests/
│       └── test_app.py          # Minimal test suite missing auth coverage
│
├── bob-evidence/                # Evidence of IBM Bob 2.0 utilization
│   ├── bob-workflow.md          # 5-phase engineering report
│   ├── screenshots/             # Generated visual proof artifacts
│   └── prompts/                 # Original engineering prompts
│
├── docs/                        # Complete technical documentation
│   ├── architecture.md          # Mermaid diagrams & system design
│   ├── api.md                   # REST API reference with curl examples
│   └── demo-script.md           # 10-step judge walkthrough script
│
├── .gitignore
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Backend Setup

```bash
# Navigate to backend directory
cd backend

# (Optional) Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy template and add your GROQ_API_KEY from https://console.groq.com
cp .env.example .env
```

Start the FastAPI development server:
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at: `http://127.0.0.1:8000/docs`

---

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Flutter dependencies
flutter pub get

# Launch Flutter app (Chrome, Desktop, or Mobile)
flutter run -d chrome
```

---

### 3. Testing the End-to-End Workflow

1. Open `http://localhost:8000/docs` to test endpoints directly or use the Flutter UI.
2. Upload `demo-project.zip` via `POST /projects/upload`.
3. Trigger analysis via `POST /projects/{id}/analyze`.
4. Inspect the detected vulnerabilities in `app.py` (Line 42 JWT flaw, Line 4 hardcoded credentials).
5. Generate a fix via `POST /issues/fix`.
6. Run AST verification via `POST /projects/{id}/verify`.
7. Generate the final release report via `POST /projects/{id}/report`.

---

## 🏆 48-Hour Hackathon Checklist

- [x] Flutter Material 3 Dashboard & Visual Charts
- [x] FastAPI REST API with complete CRUD & upload pipeline
- [x] Groq `llama-3.3-70b` integration with structured JSON mode
- [x] Zero-RCE Python AST syntax verification
- [x] Zip Slip directory traversal security protection
- [x] Supabase PostgreSQL relational schema & RLS policies
- [x] Realistic flawed `demo-project` for live demonstrations
- [x] Verifiable IBM Bob 2.0 attribution evidence
