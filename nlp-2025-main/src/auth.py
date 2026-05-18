import sqlite3
from datetime import datetime, timedelta

DB_FILE = "app_limits.db"

def init_db():
    """Initializes the SQLite database with user and logs tables."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # 1. Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                daily_limit INTEGER DEFAULT 5
            )
        """)

        # 2. Request logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS request_logs (
                username TEXT,
                timestamp TEXT
            )
        """)

        # 3. Insert a default test user (password is 'password123')
        cursor.execute("""
            INSERT OR IGNORE INTO users (username, password, daily_limit)
            VALUES ('mwawrzy1', 'password123', 5)
        """)
        conn.commit()

def verify_user(username, password) -> bool:
    """Verifies user credentials against the database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        return row is not None and row[0] == password

def check_and_increment_limit(username) -> tuple[bool, int, int]:
    """
    Checks the user's last 24-hour request count.
    Returns: (is_allowed, current_use_count, max_allowed_limit)
    """
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()

        # Get the specific user's max allowed daily limit
        cursor.execute("SELECT daily_limit FROM users WHERE username = ?", (username,))
        row = cursor.fetchone()
        if not row:
            return False, 0, 0
        max_limit = row[0]

        # Count requests made in the rolling last 24 hours
        time_threshold = (datetime.now() - timedelta(days=1)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) FROM request_logs
            WHERE username = ? AND timestamp > ?
        """, (username, time_threshold))
        current_requests = cursor.fetchone()[0]

        # Block if limit is reached
        if current_requests >= max_limit:
            return False, current_requests, max_limit

        # Register the new request
        cursor.execute("""
            INSERT INTO request_logs (username, timestamp)
            VALUES (?, ?)
        """, (username, datetime.now().isoformat()))
        conn.commit()

        return True, current_requests + 1, max_limit