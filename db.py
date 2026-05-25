import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "project_data"
DEFAULT_DB_PATH = DATA_DIR / "study_monitor.db"


def now_text():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class Database:
    """SQLite data access layer for users, logs, and detection records."""

    def __init__(self, db_path=DEFAULT_DB_PATH):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_tables()

    @contextmanager
    def connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_tables(self):
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('admin', 'user')),
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS operation_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT NOT NULL,
                    detail TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS detection_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    source TEXT NOT NULL,
                    summary_json TEXT NOT NULL,
                    alerts_json TEXT NOT NULL,
                    output_path TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS model_resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    url TEXT,
                    local_path TEXT,
                    status TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def create_user(self, username, password_hash, salt, role="user"):
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO users(username, password_hash, salt, role, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (username, password_hash, salt, role, now_text()),
            )
            return cursor.lastrowid

    def get_user_by_username(self, username):
        with self.connect() as conn:
            row = conn.execute(
                "SELECT * FROM users WHERE username = ?", (username,)
            ).fetchone()
            return dict(row) if row else None

    def get_user_by_id(self, user_id):
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return dict(row) if row else None

    def list_users(self):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, username, role, created_at
                FROM users
                ORDER BY id
                """
            ).fetchall()
            return [dict(row) for row in rows]

    def update_user_password(self, username, password_hash, salt):
        with self.connect() as conn:
            cursor = conn.execute(
                """
                UPDATE users
                SET password_hash = ?, salt = ?
                WHERE username = ?
                """,
                (password_hash, salt, username),
            )
            return cursor.rowcount

    def delete_user(self, username):
        with self.connect() as conn:
            cursor = conn.execute("DELETE FROM users WHERE username = ?", (username,))
            return cursor.rowcount

    def log_operation(self, user_id, action, detail=""):
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO operation_logs(user_id, action, detail, created_at)
                VALUES (?, ?, ?, ?)
                """,
                (user_id, action, detail, now_text()),
            )
            return cursor.lastrowid

    def list_operation_logs(self, limit=100):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT operation_logs.id, users.username, operation_logs.action,
                       operation_logs.detail, operation_logs.created_at
                FROM operation_logs
                LEFT JOIN users ON users.id = operation_logs.user_id
                ORDER BY operation_logs.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]

    def record_detection(self, user_id, source, summary, alerts, output_path=None):
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO detection_records(
                    user_id, source, summary_json, alerts_json, output_path, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    source,
                    json.dumps(summary, ensure_ascii=False),
                    json.dumps(alerts, ensure_ascii=False),
                    str(output_path) if output_path else None,
                    now_text(),
                ),
            )
            return cursor.lastrowid

    def list_detection_records(self, limit=100):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT detection_records.id, users.username, detection_records.source,
                       detection_records.summary_json, detection_records.alerts_json,
                       detection_records.output_path, detection_records.created_at
                FROM detection_records
                LEFT JOIN users ON users.id = detection_records.user_id
                ORDER BY detection_records.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [dict(row) for row in rows]

    def upsert_model_resource(self, name, url, local_path, status):
        with self.connect() as conn:
            conn.execute(
                """
                INSERT INTO model_resources(name, url, local_path, status, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    url = excluded.url,
                    local_path = excluded.local_path,
                    status = excluded.status,
                    updated_at = excluded.updated_at
                """,
                (name, url, str(local_path) if local_path else None, status, now_text()),
            )

    def list_model_resources(self):
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT id, name, url, local_path, status, updated_at
                FROM model_resources
                ORDER BY id DESC
                """
            ).fetchall()
            return [dict(row) for row in rows]
