from fastapi import FastAPI
from database import init_db, log_event, get_logs

app = FastAPI(title="Baaz Ki Nazar API")

# Initialize SQLite DB on startup
init_db()

@app.get("/")
def home():
    return {"message": "Baaz Ki Nazar API is running"}

@app.post("/alert")
def trigger_alert(violation_type: str, status: str):
    log_event(violation_type, status)
    return {"status": "Logged", "violation": violation_type, "level": status}

@app.get("/logs")
def fetch_logs():
    return {"logs": get_logs()}