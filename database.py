import sqlite3
from datetime import datetime

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    language TEXT,
    subscribed INTEGER,
    subscribed_at TEXT
)
""")
conn.commit()


def get_user(user_id: int):
    cursor.execute(
        "SELECT user_id, language, subscribed FROM users WHERE user_id = ?",
        (user_id,)
    )
    return cursor.fetchone()


def create_or_update_user(user_id: int, language: str):
    cursor.execute("""
    INSERT INTO users (user_id, language, subscribed)
    VALUES (?, ?, 0)
    ON CONFLICT(user_id) DO UPDATE SET language=excluded.language
    """, (user_id, language))
    conn.commit()


def activate_subscription(user_id: int):
    cursor.execute("""
    UPDATE users
    SET subscribed = 1, subscribed_at = ?
    WHERE user_id = ?
    """, (datetime.now().isoformat(), user_id))
    conn.commit()


def is_subscribed(user_id: int) -> bool:
    cursor.execute(
        "SELECT subscribed FROM users WHERE user_id = ?",
        (user_id,)
    )
    result = cursor.fetchone()
    return bool(result and result[0])