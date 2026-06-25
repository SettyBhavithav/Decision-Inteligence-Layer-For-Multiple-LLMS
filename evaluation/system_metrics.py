import time
import tracemalloc
import numpy as np
from typing import List

class SystemMetrics:
    """Category 7: Overall System — E2E Latency, Tokens, Cost, Memory, Throughput."""
    def __init__(self, cost_per_1k_tokens: float = 0.0005):
        self.cost_per_1k_tokens = cost_per_1k_tokens
        self.e2e_latencies: List[float] = []     # per-workflow seconds
        self.total_tokens_per_run: List[int] = []
        self.peak_memory_mb: List[float] = []    # recorded per run
        self._wall_start: float = 0.0
        self._mem_started: bool = False

    def start_run(self) -> None:
        self._wall_start = time.time()
        tracemalloc.start()
        self._mem_started = True

    def end_run(self, total_tokens: int) -> None:
        latency = time.time() - self._wall_start
        self.e2e_latencies.append(latency)
        self.total_tokens_per_run.append(total_tokens)
        if self._mem_started:
            _, peak = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            self._mem_started = False
            self.peak_memory_mb.append(peak / (1024 * 1024))

    def average_e2e_latency(self) -> float:
        return round(float(np.mean(self.e2e_latencies)), 4) if self.e2e_latencies else 0.0

    def total_tokens(self) -> int:
        return sum(self.total_tokens_per_run)

    def cost_per_workflow(self) -> float:
        avg_tokens = np.mean(self.total_tokens_per_run) if self.total_tokens_per_run else 0
        return round(float(avg_tokens / 1000.0 * self.cost_per_1k_tokens), 6)

    def average_peak_memory_mb(self) -> float:
        return round(float(np.mean(self.peak_memory_mb)), 2) if self.peak_memory_mb else 0.0

    def throughput_runs_per_second(self) -> float:
        total_time = sum(self.e2e_latencies)
        return round(len(self.e2e_latencies) / total_time, 4) if total_time > 0 else 0.0

    def summary(self) -> dict:
        return {
            "total_runs": len(self.e2e_latencies),
            "average_e2e_latency_s": self.average_e2e_latency(),
            "total_tokens_consumed": self.total_tokens(),
            "cost_per_workflow_usd": self.cost_per_workflow(),
            "average_peak_memory_mb": self.average_peak_memory_mb(),
            "throughput_runs_per_second": self.throughput_runs_per_second(),
        }
