import cv2
import sqlite3
from datetime import datetime
from fastapi import FastAPI, File, UploadFile
import numpy as np
from ultralytics import YOLO

app = FastAPI(title="Baaz Ki Nazar API")

# Load YOLO model (swap with custom trained weights if available)
model = YOLO("yolov8n.pt") 

HAZARD_CLASSES = {
    "fire": "CRITICAL_HAZARD",
    "smoke": "CRITICAL_HAZARD",
    "no_helmet": "GEAR_VIOLATION",
    "no_vest": "GEAR_VIOLATION",
    "no_goggles": "GEAR_VIOLATION"
}

def init_db():
    conn = sqlite3.connect("violations.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS violations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            violation_type TEXT,
            severity TEXT,
            confidence REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.get("/")
def read_root():
    return {"status": "Baaz Ki Nazar Backend Live"}

@app.post("/detect/")
async def detect_violations(file: UploadFile = File(...)):
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    results = model(frame, conf=0.25)
    violations = []

    conn = sqlite3.connect("violations.db")
    cursor = conn.cursor()

    for r in results:
        for box in r.boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id].lower()
            conf = float(box.conf[0])

            if label in HAZARD_CLASSES:
                severity = HAZARD_CLASSES[label]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                violations.append({
                    "type": label.upper(),
                    "severity": severity,
                    "confidence": round(conf, 2),
                    "time": timestamp
                })

                cursor.execute(
                    "INSERT INTO violations (timestamp, violation_type, severity, confidence) VALUES (?, ?, ?, ?)",
                    (timestamp, label.upper(), severity, conf)
                )

    conn.commit()
    conn.close()
    return {"status": "success", "detected_violations": violations}

@app.get("/logs/")
async def get_logs():
    conn = sqlite3.connect("violations.db")
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, violation_type, severity, confidence FROM violations ORDER BY id DESC")
    logs = cursor.fetchall()
    conn.close()
    return {"logs": logs}
