import sqlite3
import threading
from datetime import datetime, timezone

_lock = threading.Lock()

def init_db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS meetings (
        id       INTEGER PRIMARY KEY,
        title    TEXT,
        started  TEXT,
        ended    TEXT
    );
    CREATE TABLE IF NOT EXISTS segments (
        id            INTEGER PRIMARY KEY,
        meeting_id    INTEGER NOT NULL,
        ts_start      REAL NOT NULL,
        ts_end        REAL NOT NULL,
        source_lang   TEXT,
        original_text TEXT,
        english_text  TEXT NOT NULL,
        FOREIGN KEY (meeting_id) REFERENCES meetings(id)
    );
    """)
    conn.commit()
    return conn

def start_meeting(conn, title: str = "Untitled") -> int:
    with _lock:
        cur = conn.execute(
            "INSERT INTO meetings(title, started) VALUES (?, ?)",
            (title, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return cur.lastrowid

def end_meeting(conn, meeting_id: int):
    with _lock:
        conn.execute(
            "UPDATE meetings SET ended=? WHERE id=?",
            (datetime.now(timezone.utc).isoformat(), meeting_id),
        )
        conn.commit()

def insert_segment(conn, meeting_id: int, ts_start: float, ts_end: float,
                   source_lang: str | None, original: str | None, english: str) -> int:
    with _lock:
        cur = conn.execute(
            """INSERT INTO segments
               (meeting_id, ts_start, ts_end, source_lang, original_text, english_text)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (meeting_id, ts_start, ts_end, source_lang, original, english),
        )
        conn.commit()
        return cur.lastrowid
