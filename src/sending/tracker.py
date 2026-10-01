"""
Outreach Tracker and Persistence Layer.
Manages SQLite database storage, duplicate outreach suppression, and audit logs.
"""

import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import config

logger = logging.getLogger(__name__)

class OutreachTracker:
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or config.DB_PATH
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS outreach_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    influencer_id TEXT,
                    influencer_name TEXT NOT NULL,
                    platform TEXT,
                    email TEXT,
                    channel TEXT NOT NULL,
                    message_content TEXT NOT NULL,
                    status TEXT NOT NULL,
                    sent_at TEXT NOT NULL,
                    notes TEXT
                )
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_email ON outreach_logs(email)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_influencer ON outreach_logs(influencer_id)")
            conn.commit()

    def is_already_contacted(self, email: Optional[str], influencer_id: Optional[str]) -> bool:
        """
        Duplicate prevention logic: checks if email or influencer_id has an active or sent outreach.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # If email is valid, check by email
            if email and email.lower() != "not found":
                cursor.execute(
                    "SELECT COUNT(*) FROM outreach_logs WHERE LOWER(email) = LOWER(?) AND status IN ('SENT', 'SIMULATED_SENT')",
                    (email.strip(),)
                )
                if cursor.fetchone()[0] > 0:
                    return True

            # Also check by creator ID
            if influencer_id:
                cursor.execute(
                    "SELECT COUNT(*) FROM outreach_logs WHERE influencer_id = ? AND status IN ('SENT', 'SIMULATED_SENT')",
                    (influencer_id.strip(),)
                )
                if cursor.fetchone()[0] > 0:
                    return True

        return False

    def log_outreach(
        self,
        influencer_name: str,
        channel: str,
        message_content: str,
        status: str,
        email: Optional[str] = "Not Found",
        influencer_id: Optional[str] = None,
        platform: Optional[str] = "Instagram",
        notes: Optional[str] = None
    ) -> int:
        """
        Inserts an immutable audit record into the outreach database.
        """
        sent_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO outreach_logs (
                    influencer_id, influencer_name, platform, email,
                    channel, message_content, status, sent_at, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                influencer_id,
                influencer_name,
                platform,
                email or "Not Found",
                channel,
                message_content,
                status,
                sent_at,
                notes or ""
            ))
            conn.commit()
            return cursor.lastrowid

    def get_all_logs(self) -> List[Dict[str, Any]]:
        """
        Returns all tracked outreach events formatted as dictionaries.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM outreach_logs ORDER BY id DESC")
            rows = cursor.fetchall()
            return [dict(r) for r in rows]

    def clear_tracker(self):
        """
        Utility for testing: resets the outreach database.
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM outreach_logs")
            conn.commit()
