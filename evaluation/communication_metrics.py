import numpy as np
from typing import List

class CommunicationMetrics:
    """Category 5: Communication Evaluation — Messages, Filtering, Payload, Tokens, Latency, Graph Density."""
    def __init__(self):
        self.messages_sent: int = 0
        self.messages_filtered: int = 0
        self.payload_sizes: List[int] = []       # in tokens
        self.token_usages: List[int] = []
        self.latencies: List[float] = []          # seconds per routed message
        # Graph density = edges / max_possible_edges for n nodes
        self.graph_densities: List[float] = []

    def log_message(self, sent: bool, filtered: bool,
                    payload_tokens: int, latency_s: float) -> None:
        if sent:
            self.messages_sent += 1
            self.payload_sizes.append(payload_tokens)
            self.token_usages.append(payload_tokens)
            self.latencies.append(latency_s)
        if filtered:
            self.messages_filtered += 1

    def log_graph_density(self, edges: int, num_nodes: int) -> None:
        max_edges = num_nodes * (num_nodes - 1) if num_nodes > 1 else 1
        self.graph_densities.append(edges / max_edges)

    def filter_ratio(self) -> float:
        total = self.messages_sent + self.messages_filtered
        return round(self.messages_filtered / total, 4) if total > 0 else 0.0

    def average_payload_size(self) -> float:
        return round(float(np.mean(self.payload_sizes)), 2) if self.payload_sizes else 0.0

    def total_token_usage(self) -> int:
        return sum(self.token_usages)

    def average_latency(self) -> float:
        return round(float(np.mean(self.latencies)), 4) if self.latencies else 0.0

    def average_graph_density(self) -> float:
        return round(float(np.mean(self.graph_densities)), 4) if self.graph_densities else 0.0

    def summary(self) -> dict:
        return {
            "messages_sent": self.messages_sent,
            "messages_filtered": self.messages_filtered,
            "filter_ratio": self.filter_ratio(),
            "average_payload_tokens": self.average_payload_size(),
            "total_token_usage": self.total_token_usage(),
            "average_latency_s": self.average_latency(),
            "average_graph_density": self.average_graph_density(),
        }
