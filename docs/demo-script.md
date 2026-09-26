# DevFlow 48-Hour Hackathon Demo Script

Follow this step-by-step live presentation walkthrough during judge evaluations.

---

## Pre-Demo Checklist (30 seconds before judging)
1. **Backend Server running**:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
2. **Frontend running**:
   ```bash
   cd frontend
   flutter run -d chrome  # or windows / android
   ```
3. Have `demo-project.zip` ready on desktop or in `devflow/demo-project.zip`.

---

## 10-Step Interactive Judge Demonstration

### Step 1: Open DevFlow Dashboard
- **Action**: Launch the Flutter DevFlow application.
- **Talking Point**:
  > *"Welcome to DevFlow. Modern engineering teams waste hundreds of hours reviewing code for security flaws, debugging regressions, and arguing over release readiness. DevFlow is an automated release gatekeeper and AI remediation engine."*
- **Visual**: Show the recent analyses dashboard, health scores (85, 72, 98), and dark Material 3 design.

---

### Step 2: Upload Intentionally Flawed Project
- **Action**: Click **"Analyze Project"** or upload `demo-project.zip`.
- **Talking Point**:
  > *"We've uploaded a representative Python microservice (`demo-project.zip`). Notice that our backend features Zip Slip protection to ensure arbitrary archive paths can never escape into the host environment."*

---

### Step 3: Trigger Groq AI Analysis
- **Action**: Click **"ANALYZE"**.
- **Talking Point**:
  > *"DevFlow indexes the codebase and triggers Groq's high-throughput `llama-3.3-70b-versatile` model with structured JSON enforcement."*
- **Visual**: Show the Health Score gauge drop to **61 / 100** with categorized breakdown:
  - 🐛 Bugs: 1
  - 🔐 Security: 2
  - 🧪 Tests: 1
  - 🧹 Maintainability: 1

---

### Step 4: Inspect Critical Security Issue
- **Action**: Click on **"Hard-coded credentials & plain text authentication"** or **"JWT authentication vulnerability"** (`app.py • Line 42`).
- **Talking Point**:
  > *"Notice how DevFlow pinpoints exact file and line numbers: in `app.py`, line 42, JWT decoding occurs with signature verification disabled, allowing token forgery."*
- **Visual**: Highlight the code snippet showing:
  ```python
  payload = jwt.decode(token, options={"verify_signature": False})
  ```

---

### Step 5: Generate AI Remediation Plan
- **Action**: Click **"Generate AI Fix Plan"**.
- **Talking Point**:
  > *"Rather than just pointing out problems, DevFlow synthesizes a safe fix plan: root cause analysis, files to change, and a unified diff."*
- **Visual**: Show the animated 4-step workflow:
  1. Identify vulnerable code
  2. Generate correction
  3. Generate regression test
  4. Verify correction

---

### Step 6: Generate Regression Tests
- **Action**: Show the synthesized test cases.
- **Talking Point**:
  > *"DevFlow doesn't just patch code; it synthesizes regression unit tests to prevent this vulnerability from resurfacing in future pull requests."*

---

### Step 7: Execute Safe AST Verification Gate
- **Action**: Click **"VERIFY"**.
- **Talking Point**:
  > *"A critical safety guarantee: DevFlow NEVER executes arbitrary uploaded code in the review pipeline. Instead, we use Python's native AST parser (`ast.parse`) to safely verify syntax integrity."*
- **Visual**: Show **"VERIFICATION PASSED ✅"** with 2 of 2 files validated.

---

### Step 8: View Executive Release Readiness Report
- **Action**: Open the Release Report modal.
- **Talking Point**:
  > *"DevFlow combines AST verification results with remaining vulnerabilities to generate an executive release gatekeeper decision. In this case, the release is blocked until the 2 critical security issues are patched."*

---

### Step 9: Showcase IBM Bob 2.0 Attribution
- **Action**: Open `bob-evidence/bob-workflow.md` and show `bob-evidence/screenshots/`.
- **Talking Point**:
  > *"We want to be 100% transparent about our AI architecture: Groq powers runtime AI inside DevFlow, while IBM Bob 2.0 was our autonomous AI software engineer used throughout the hackathon for architecture design, Zip Slip debugging, AST verification, and documentation."*

---

### Step 10: Judge Q&A Prep
- **Q: Does DevFlow run Docker or untrusted code?**
  - **A**: *"No, our verification gate is pure AST static analysis. Untrusted code is never executed on the host."*
- **Q: How does the backend communicate with Supabase?**
  - **A**: *"All database operations are encapsulated in `supabase_service.py` with PostgreSQL Row Level Security (RLS) policies and automatic local in-memory fallback for offline resilience."*
