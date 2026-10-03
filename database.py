import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("safety_logs.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            violation_type TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_event(violation_type, status):
    conn = sqlite3.connect("safety_logs.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (timestamp, violation_type, status) VALUES (?, ?, ?)",
                   (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), violation_type, status))
    conn.commit()
    conn.close()

def get_logs():
    conn = sqlite3.connect("safety_logs.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows

if __name__ == "__main__":
    init_db()