import numpy as np
from typing import Dict, List

class TrustMetrics:
    """Category 2: Trust Evaluation — Avg Trust, Stability, Convergence, Recovery."""
    def __init__(self):
        # Per-agent trust score history: {role: [score_0, score_1, ...]}
        self.histories: Dict[str, List[float]] = {}
        # Steps at which each agent converged (within threshold of final value)
        self.convergence_steps: Dict[str, int] = {}
        # Recovery: (pre_failure_trust, post_recovery_trust) per event
        self.recovery_events: List[tuple] = []

    def log_trust(self, role: str, score: float) -> None:
        self.histories.setdefault(role, []).append(score)

    def log_recovery_event(self, pre_failure: float, post_recovery: float) -> None:
        self.recovery_events.append((pre_failure, post_recovery))

    def average_trust(self) -> Dict[str, float]:
        return {r: round(float(np.mean(h)), 4) for r, h in self.histories.items() if h}

    def trust_stability(self) -> Dict[str, float]:
        """Lower std = more stable trust."""
        return {r: round(float(np.std(h)), 4) for r, h in self.histories.items() if h}

    def trust_convergence(self, threshold: float = 0.02) -> Dict[str, int]:
        """Step index at which trust scores stop fluctuating beyond threshold."""
        result = {}
        for role, h in self.histories.items():
            if len(h) < 3:
                result[role] = len(h)
                continue
            final = h[-1]
            conv_step = len(h)
            for i in range(len(h) - 2, -1, -1):
                if abs(h[i] - final) > threshold:
                    conv_step = i + 1
                    break
            result[role] = conv_step
        return result

    def trust_recovery_rate(self) -> float:
        """Fraction of recovery events where post_recovery >= pre_failure trust."""
        if not self.recovery_events:
            return 0.0
        recovered = sum(1 for pre, post in self.recovery_events if post >= pre * 0.90)
        return round(recovered / len(self.recovery_events), 4)

    def summary(self) -> dict:
        return {
            "average_trust": self.average_trust(),
            "trust_stability_std": self.trust_stability(),
            "trust_convergence_step": self.trust_convergence(),
            "trust_recovery_rate": self.trust_recovery_rate(),
        }
