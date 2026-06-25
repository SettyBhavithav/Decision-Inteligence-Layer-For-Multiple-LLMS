import os
import sqlite3
import logging

logger = logging.getLogger("trust_framework")

class DatabaseConnection:
    """
    Manages SQLite database connection and initial schema configuration.
    """
    def __init__(self, db_path: str = "metadata.db"):
        self.db_path = db_path
        self._init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        """Initializes relational SQL database tables."""
        with self.get_connection() as conn:
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
            
            # Subtasks Execution Table
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
            
            # Failure Attribution Table
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
        logger.info(f"DatabaseConnection: SQLite database initialized at {self.db_path}")

    def clear_database(self) -> None:
        """Clears all records for cleaning the environment."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM subtasks")
            cursor.execute("DELETE FROM trust_history")
            cursor.execute("DELETE FROM failures")
            conn.commit()
        logger.info("DatabaseConnection: All database records cleared.")
