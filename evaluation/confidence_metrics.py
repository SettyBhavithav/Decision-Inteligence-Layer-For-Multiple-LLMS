import numpy as np
from typing import List, Tuple

class ConfidenceMetrics:
    """Category 3: Confidence Evaluation — Avg Confidence, ECE, Stability, Claim Accuracy."""
    def __init__(self):
        # (predicted_confidence, actual_success_label: 0/1)
        self.data: List[Tuple[float, int]] = []
        # Claim-level: (claim_confidence, claim_verified: bool)
        self.claim_data: List[Tuple[float, bool]] = []

    def log_confidence(self, confidence: float, success: bool) -> None:
        self.data.append((confidence, 1 if success else 0))

    def log_claim(self, confidence: float, verified: bool) -> None:
        self.claim_data.append((confidence, verified))

    def average_confidence(self) -> float:
        if not self.data:
            return 0.0
        return round(float(np.mean([c for c, _ in self.data])), 4)

    def confidence_stability(self) -> float:
        """Lower std = more stable confidence estimates."""
        if not self.data:
            return 0.0
        return round(float(np.std([c for c, _ in self.data])), 4)

    def ece(self, n_bins: int = 5) -> float:
        """Expected Calibration Error."""
        if not self.data:
            return 0.0
        confs = np.array([c for c, _ in self.data])
        labels = np.array([l for _, l in self.data])
        ece_val = 0.0
        bins = np.linspace(0, 1, n_bins + 1)
        for i in range(n_bins):
            mask = (confs >= bins[i]) & (confs < bins[i + 1])
            prop = np.mean(mask)
            if prop > 0:
                acc = np.mean(labels[mask])
                avg_conf = np.mean(confs[mask])
                ece_val += prop * abs(avg_conf - acc)
        return round(float(ece_val), 4)

    def claim_level_accuracy(self) -> float:
        """Fraction of claims where confidence correctly predicted verification outcome."""
        if not self.claim_data:
            return 0.0
        # Correct: high-conf claim is verified, low-conf claim is not
        correct = sum(1 for c, v in self.claim_data if (c >= 0.5) == v)
        return round(correct / len(self.claim_data), 4)

    def summary(self) -> dict:
        return {
            "average_confidence": self.average_confidence(),
            "confidence_stability_std": self.confidence_stability(),
            "ece": self.ece(),
            "claim_level_accuracy": self.claim_level_accuracy(),
        }
