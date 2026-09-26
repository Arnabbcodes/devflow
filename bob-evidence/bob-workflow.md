# IBM Bob 2.0 Engineering Workflow & Evidence

This document records the exact role and utilization of **IBM Bob 2.0** throughout the conception, architecture, implementation, and hardening of **DevFlow**.

---

## Architecture Distinction
> **Critical Architectural Clarification**:
> - **Groq (llama-3.3-70b-versatile)**: Powers the **runtime AI intelligence** within the DevFlow application (dynamic code analysis, fix generation, test synthesis, and release reporting).
> - **IBM Bob 2.0**: Was utilized as the **autonomous AI software engineering companion** used by the development team to architect, implement, debug, and document the entire DevFlow platform during the hackathon.

---

## 1. Architecture Phase
- **Challenge**: Defining clean separation of concerns across Flutter frontend, FastAPI backend, Groq AI inference, safe AST verification, and Supabase persistence.
- **Bob's Role**:
  - Analyzed the hackathon scope and structured the project into modular sub-packages (`ai`, `services`, `utils`, `schemas`, `config`).
  - Proposed the AST verification architecture to avoid risky remote code execution during automated reviews.
  - Guided the database schema design (`profiles`, `projects`, `analyses`, `issues`, `fixes`, `verification_results`) and Row-Level Security (RLS) policies.

## 2. Development Phase
- **Challenge**: Building standard Pydantic schemas, Groq API client with JSON-mode enforcement, and zero-leak ZIP upload extraction.
- **Bob's Role**:
  - Authored the asynchronous `groq_client.py` using `httpx` with timeout management and clear error reporting.
  - Formatted prompt engineering structures (`ANALYSIS_SYSTEM`, `FIX_SYSTEM`, `TESTS_SYSTEM`, `REPORT_SYSTEM`) with rigid JSON schemas for Flutter rendering.
  - Implemented the in-memory/Supabase hybrid data access layer in `supabase_service.py` ensuring graceful degradation if external services are unreachable.

## 3. Debugging Phase
- **Challenge**: Protecting the server against malicious or malformed ZIP archives containing directory traversal attacks (Zip Slip).
- **Bob's Role**:
  - Identified vulnerability vectors in standard `zipfile.extractall`.
  - Authored `zip_handler.py` with explicit Path boundary checks (`relative_to` and `os.path.commonpath`) to completely eliminate Zip Slip vulnerabilities.
  - Provided regex-based JSON extraction fallback in `file_parser.py` to handle LLMs that enclose JSON in markdown backticks.

## 4. Testing Phase
- **Challenge**: Designing a realistic, intentionally imperfect demo project with clear security and maintainability flaws that can be evaluated live.
- **Bob's Role**:
  - Created `demo-project/` containing hardcoded secrets (`SECRET = "demo-secret"`), unvalidated JWT signatures, and bare `except Exception: pass`.
  - Designed the AST verification unit tests to validate syntax correctness across extracted project code.

## 5. Documentation Phase
- **Challenge**: Preparing technical artifacts and an interactive live demo script for hackathon judging.
- **Bob's Role**:
  - Authored the complete system architecture diagram in `docs/architecture.md`.
  - Documented all 10 REST API endpoints with request/response schemas in `docs/api.md`.
  - Crafted the 10-step judge demonstration walkthrough in `docs/demo-script.md`.
