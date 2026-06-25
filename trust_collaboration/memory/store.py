import os
import sqlite3
import logging
from typing import Dict, Any, List

logger = logging.getLogger("trust_framework")

class MemoryStore:
    """
    Memory Manager (Layer 7).
    SQLAlchemy/SQLite implementation to store tasks, trust history,
    conversations, and failure logs.
    """
    def __init__(self, db_path: str = "metadata.db"):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Conversations Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    query TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Subtasks Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subtasks (
                    id TEXT PRIMARY KEY,
                    conversation_id TEXT,
                    description TEXT,
                    role TEXT,
                    status TEXT,
                    response TEXT,
                    confidence REAL,
                    calibrated_conf REAL,
                    trust REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Trust History Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trust_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_role TEXT,
                    score REAL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Failures Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS failures (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT,
                    responsible_role TEXT,
                    step_index INTEGER,
                    reason TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
        logger.info(f"MemoryStore: Initialized SQLite database at {self.db_path}")

    def save_conversation(self, conv_id: str, query: str, response: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO conversations (id, query, response) VALUES (?, ?, ?)",
                (conv_id, query, response)
            )
            conn.commit()

    def save_subtask(self, 
                     task_id: str, 
                     conv_id: str, 
                     desc: str, 
                     role: str, 
                     status: str, 
                     resp: str, 
                     conf: float, 
                     calibrated_conf: float, 
                     trust: float) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO subtasks 
                   (id, conversation_id, description, role, status, response, confidence, calibrated_conf, trust) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (task_id, conv_id, desc, role, status, resp, conf, calibrated_conf, trust)
            )
            conn.commit()

    def log_trust(self, role: str, score: float) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO trust_history (agent_role, score) VALUES (?, ?)",
                (role, score)
            )
            conn.commit()

    def log_failure(self, conv_id: str, resp_role: str, step_index: int, reason: str) -> None:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO failures (conversation_id, responsible_role, step_index, reason) VALUES (?, ?, ?, ?)",
                (conv_id, resp_role, step_index, reason)
            )
            conn.commit()

    def get_conversation(self, conv_id: str) -> Dict[str, Any]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            res = cursor.execute("SELECT * FROM conversations WHERE id = ?", (conv_id,)).fetchone()
            return dict(res) if res else {}

    def get_trust_history(self, role: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            res = cursor.execute(
                "SELECT score, timestamp FROM trust_history WHERE agent_role = ? ORDER BY timestamp ASC",
                (role.lower(),)
            ).fetchall()
            return [dict(row) for row in res]

    def get_all_failures(self) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            res = cursor.execute("SELECT * FROM failures ORDER BY timestamp DESC").fetchall()
            return [dict(row) for row in res]
            
    def clear_database(self) -> None:
        """Clear all data for clean runs."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM subtasks")
            cursor.execute("DELETE FROM trust_history")
            cursor.execute("DELETE FROM failures")
            conn.commit()
        logger.info("MemoryStore: Database cleared.")
