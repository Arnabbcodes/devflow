from fastapi import FastAPI, HTTPException, Header
import jwt

SECRET = "demo-secret"
DATABASE_URL = "sqlite:///./demo.db"

app = FastAPI(title="Demo Vulnerable API")


@app.get("/")
def read_root():
    return {"status": "running", "service": "user-auth"}


@app.post("/login")
def login(username: str, password: str):
    # Flaw 1: Hardcoded credentials & plaintext comparison
    if username == "admin" and password == "admin123":
        token = jwt.encode({"sub": username, "role": "admin"}, SECRET, algorithm="HS256")
        return {"token": token}
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/profile")
def get_profile(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    # Flaw 2: Missing signature verification (Line 42 area)
    # Allows attackers to forge tokens arbitrarily
    payload = jwt.decode(token, options={"verify_signature": False})
    return {"user": payload.get("sub"), "role": payload.get("role")}


@app.post("/process-data")
def process_data(data: dict):
    # Flaw 3: Silent catch-all exception swallows errors
    try:
        result = int(data.get("value", 0)) * 100
        return {"result": result}
    except Exception:
        # Silently fails, masking potential TypeError or AttributeError
        pass
    return {"result": 0}
