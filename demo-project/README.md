# Demo Project (DevFlow Evaluation Target)

This is an intentionally flawed microservice used to demonstrate the automated auditing, security analysis, and verification capabilities of **DevFlow**.

### Known Intentional Flaws:
1. **Hardcoded Credentials**: Admin credentials and signing secret hardcoded in `app.py`.
2. **Insecure Authentication**: JWT signature verification disabled (`verify_signature: False`).
3. **Broad Exception Handling**: Bare `except Exception: pass` masking internal errors.
4. **Missing Tests**: Sparse test coverage missing negative authentication flows.
5. **Unpinned Dependencies**: `requirements.txt` lacks version pinning.
