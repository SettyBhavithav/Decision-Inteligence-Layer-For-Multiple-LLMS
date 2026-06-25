import logging
import numpy as np
from typing import List, Dict, Any
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger("trust_framework")

class ConfidenceEstimator:
    """
    Confidence Estimation Engine (DIL Module 2).
    Evaluates and calibrates self-reported confidence using Platt scaling over trajectory features:
    [self_reported_confidence, structural_consistency, step_index, accumulated_failures]
    """
    def __init__(self):
        self.calibrator = LogisticRegression()
        self.is_trained = False
        
        # Default fallback weights if not trained
        self.default_w = np.array([0.7, 0.2, -0.05, -0.1])
        self.default_b = 0.1

    def estimate_structural_confidence(self, response: str, reasoning: str) -> float:
        """
        Calculates structural confidence based on text consistency and length.
        """
        uncertainty_words = ["maybe", "perhaps", "not sure", "unsure", "likely", "unlikely", "hallucination", "error", "fail", "possibly"]
        text = (response + " " + reasoning).lower()
        
        count = sum(1 for word in uncertainty_words if word in text)
        score = 1.0 - (count * 0.1)
        
        if len(response.strip()) < 10:
            score -= 0.5
            
        return max(0.0, min(1.0, score))

    def calibrate(self, 
                  self_conf: float, 
                  structural_conf: float, 
                  step_index: int, 
                  accum_failures: int) -> float:
        """
        Predict calibrated confidence using Logistic Regression.
        """
        features = np.array([[self_conf, structural_conf, float(step_index), float(accum_failures)]])
        
        if self.is_trained:
            try:
                prob = self.calibrator.predict_proba(features)[0][1]
                return float(prob)
            except Exception as e:
                logger.warning(f"Platt scaling prediction failed: {e}. Falling back to default calibration.")
        
        # Fallback linear model + sigmoid
        z = np.dot(features[0], self.default_w) + self.default_b
        prob = 1.0 / (1.0 + np.exp(-z))
        return float(prob)

    def train_calibrator(self, X_train: List[List[float]], y_train: List[int]) -> bool:
        """
        Train the calibrator on historical execution features.
        """
        if len(X_train) < 5:
            logger.info("Confidence Estimator: Insufficient training data to train calibrator (need at least 5 samples).")
            return False
            
        if len(set(y_train)) < 2:
            logger.info("Confidence Estimator: Training data must contain both success and failure cases to train calibrator.")
            return False
            
        try:
            X = np.array(X_train)
            y = np.array(y_train)
            self.calibrator.fit(X, y)
            self.is_trained = True
            logger.info("Confidence Estimator: Platt scaling calibrator trained successfully.")
            return True
        except Exception as e:
            logger.error(f"Confidence Estimator training error: {e}")
            return False
            
    def get_calibration_details(self) -> Dict[str, Any]:
        """Return model coefficients for transparency."""
        if self.is_trained:
            return {
                "is_trained": True,
                "coefficients": self.calibrator.coef_[0].tolist(),
                "intercept": float(self.calibrator.intercept_[0])
            }
        return {
            "is_trained": False,
            "coefficients": self.default_w.tolist(),
            "intercept": self.default_b
        }
