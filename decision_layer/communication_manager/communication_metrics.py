import time
from typing import List, Dict, Any
from decision_layer.communication_manager.models import CommunicationMetrics
from decision_layer.communication_manager.communication_store import CommunicationStore

class CommunicationMetricsTracker:
    """Submodule 10: Telemetry logger tracking token counts, latencies, and connection graph densities."""
    def __init__(self, store: CommunicationStore):
        self.store = store
        self.start_time = 0.0
        self.latency = 0.0
        self.total_messages = 0
        self.filtered_messages = 0
        self.total_payload_size = 0
        self.token_consumption = 0

    def start_timer(self) -> None:
        self.start_time = time.time()

    def stop_timer(self) -> None:
        self.latency = time.time() - self.start_time

    def log_message(self, size: int, filtered: bool = False, tokens: int = 0) -> None:
        self.total_messages += 1
        if filtered:
            self.filtered_messages += 1
        else:
            self.total_payload_size += size
            self.token_consumption += tokens

    def compile_metrics(self) -> CommunicationMetrics:
        # Calculate graph density: Edges / (Nodes * (Nodes - 1))
        nodes = len(self.store.get_nodes())
        edges = len(self.store.get_edges())
        density = 0.0
        if nodes > 1:
            density = edges / (nodes * (nodes - 1))
            
        avg_size = 0.0
        active_msgs = self.total_messages - self.filtered_messages
        if active_msgs > 0:
            avg_size = self.total_payload_size / active_msgs
            
        return CommunicationMetrics(
            total_messages=self.total_messages,
            filtered_messages=self.filtered_messages,
            average_payload_size=avg_size,
            communication_latency=self.latency,
            token_consumption=self.token_consumption,
            graph_density=density
        )
