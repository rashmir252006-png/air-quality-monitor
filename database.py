import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password_hash TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            city TEXT,
            aqi INTEGER,
            co REAL,
            no2 REAL,
            o3 REAL,
            so2 REAL,
            pm2_5 REAL,
            pm10 REAL,
            nh3 REAL,
            searched_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (email, password_hash, created_at) VALUES (?, ?, ?)",
            (email, hash_password(password), datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def verify_user(email, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE email = ?", (email,))
    row = cursor.fetchone()
    conn.close()
    if row is None:
        return False
    return row[0] == hash_password(password)

def save_search(user_email, data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO history (user_email, city, aqi, co, no2, o3, so2, pm2_5, pm10, nh3, searched_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_email, data["city"], data["aqi"], data["co"], data["no2"], data["o3"],
        data["so2"], data["pm2_5"], data["pm10"], data["nh3"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def get_history(user_email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM history WHERE user_email = ? ORDER BY id DESC", (user_email,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_city_history(user_email, city):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM history WHERE user_email = ? AND city = ? ORDER BY id ASC",
        (user_email, city)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_distinct_cities(user_email):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT city FROM history WHERE user_email = ?", (user_email,))
    rows = [r[0] for r in cursor.fetchall()]
    conn.close()
    return rows