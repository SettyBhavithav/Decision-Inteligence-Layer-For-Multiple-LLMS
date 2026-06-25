import logging
from typing import Dict, Any, List
from database.connection import DatabaseConnection

logger = logging.getLogger("trust_framework")

class LongTermMemory:
    """
    Long-Term Memory Manager (Layer 6 Module 6 / Layer 7).
    Persists finalized session outputs, trust trajectories, and failure reports.
    """
    def __init__(self, db_conn: DatabaseConnection):
        self.db_conn = db_conn

    def save_conversation(self, conversation_id: str, query: str, response: str) -> None:
        """Saves a finalized query and corresponding aggregated response."""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO conversations (id, query, response) VALUES (?, ?, ?)",
                (conversation_id, query, response)
            )
            conn.commit()
        logger.info(f"LongTermMemory: Persisted conversation {conversation_id}")

    def log_trust_transition(self, role: str, score: float) -> None:
        """Appends a trust update event for research evaluation."""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO trust_history (agent_role, score) VALUES (?, ?)",
                (role.lower(), score)
            )
            conn.commit()

    def log_failure_attribution(self, conversation_id: str, resp_role: str, step_index: int, reason: str) -> None:
        """Appends a failure attribution event to database memory."""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO failures (conversation_id, responsible_role, step_index, reason) VALUES (?, ?, ?, ?)",
                (conversation_id, resp_role, step_index, reason)
            )
            conn.commit()
        logger.info(f"LongTermMemory: Failure attributed to {resp_role} at step {step_index}")

    def get_trust_history(self, role: str) -> List[Dict[str, Any]]:
        """Retrieves trust history data points for plotting."""
        with self.db_conn.get_connection() as conn:
            conn.row_factory = lambda cursor, row: {"score": row[0], "timestamp": row[1]}
            cursor = conn.cursor()
            rows = cursor.execute(
                "SELECT score, timestamp FROM trust_history WHERE agent_role = ? ORDER BY timestamp ASC",
                (role.lower(),)
            ).fetchall()
            return rows

    def get_all_failures(self) -> List[Dict[str, Any]]:
        """Retrieves failure records for logging/analysis."""
        with self.db_conn.get_connection() as conn:
            conn.row_factory = lambda cursor, row: {
                "id": row[0], "conversation_id": row[1], "responsible_role": row[2], 
                "step_index": row[3], "reason": row[4], "timestamp": row[5]
            }
            cursor = conn.cursor()
            rows = cursor.execute("SELECT * FROM failures ORDER BY timestamp DESC").fetchall()
            return rows
