import logging
from typing import Dict, Any, List
from database.connection import DatabaseConnection

logger = logging.getLogger("trust_framework")

class ShortTermMemory:
    """
    Short-Term Memory Manager (Layer 6 Module 6 / Layer 7).
    Manages intermediate subtask outputs and active execution state.
    """
    def __init__(self, db_conn: DatabaseConnection):
        self.db_conn = db_conn

    def save_subtask_state(self, 
                           task_id: str, 
                           conversation_id: str, 
                           description: str, 
                           role: str, 
                           status: str, 
                           response: str, 
                           confidence: float, 
                           calibrated_conf: float, 
                           trust: float) -> None:
        """Saves intermediate subtask response and metrics into active memory."""
        with self.db_conn.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO subtasks 
                   (id, conversation_id, description, role, status, response, confidence, calibrated_conf, trust) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (task_id, conversation_id, description, role, status, response, confidence, calibrated_conf, trust)
            )
            conn.commit()
        logger.debug(f"ShortTermMemory: Saved state for {task_id} ({role}) with status {status}")

    def get_subtask_responses(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Retrieves all intermediate subtask results for an active conversation."""
        with self.db_conn.get_connection() as conn:
            conn.row_factory = lambda cursor, row: {
                col[0]: row[idx] for idx, col in enumerate(cursor.description)
            }
            cursor = conn.cursor()
            rows = cursor.execute(
                "SELECT * FROM subtasks WHERE conversation_id = ? ORDER BY timestamp ASC",
                (conversation_id,)
            ).fetchall()
            return rows
