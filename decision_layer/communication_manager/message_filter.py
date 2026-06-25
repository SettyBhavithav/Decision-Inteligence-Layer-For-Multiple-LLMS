import logging
from typing import Dict, Any, List

logger = logging.getLogger("trust_framework")

class MessageFilter:
    """Submodule 4: Filters duplicate content, empty payloads, and obsolete contexts."""
    def __init__(self):
        self._sent_payload_hashes = set()

    def should_filter(self, payload: Dict[str, Any]) -> bool:
        if not payload:
            logger.warning("MessageFilter: Blocked empty payload message.")
            return True
            
        content = payload.get("content", "").strip()
        if not content:
            logger.warning("MessageFilter: Blocked empty string context.")
            return True
            
        payload_hash = hash(content)
        if payload_hash in self._sent_payload_hashes:
            logger.warning("MessageFilter: Blocked redundant message (duplicate hash).")
            return True
            
        # Register hash to avoid duplicates later
        self._sent_payload_hashes.add(payload_hash)
        return False
