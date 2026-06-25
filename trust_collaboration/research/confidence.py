import logging
import numpy as np
from typing import List, Dict, Any
from sklearn.linear_model import LogisticRegression

logger = logging.getLogger("trust_framework")

class ConfidenceEstimator:
    """
    Estimates and calibrates agent confidence scores.
    Uses Platt scaling (logistic regression) over trajectory features:
    [self_reported_confidence, structural_consistency, step_index, accumulated_failures]
    """
    def __init__(self):
        # Platt scaling model
        self.calibrator = LogisticRegression()
        self.is_trained = False
        
        # Default fallback weights if not trained
        self.default_w = np.array([0.7, 0.2, -0.05, -0.1])
        self.default_b = 0.1

    def estimate_structural_confidence(self, response: str, reasoning: str) -> float:
        """
        Compute structural confidence based on heuristics:
        - length, presence of uncertainty keywords, reasoning density, etc.
        """
        uncertainty_words = ["maybe", "perhaps", "not sure", "unsure", "likely", "unlikely", "hallucination", "error", "fail", "possibly"]
        text = (response + " " + reasoning).lower()
        
        # Count uncertainty indicators
        count = sum(1 for word in uncertainty_words if word in text)
        
        # Baseline structural score
        score = 1.0 - (count * 0.1)
        
        # Adjust for empty or extremely short response
        if len(response.strip()) < 10:
            score -= 0.5
            
        return max(0.0, min(1.0, score))

    def calibrate(self, 
                  self_conf: float, 
                  structural_conf: float, 
                  step_index: int, 
                  accum_failures: int) -> float:
        """
        Compute the calibrated confidence score using Platt scaling.
        If the calibrator is not trained, fall back to a linear model + sigmoid.
        """
        features = np.array([[self_conf, structural_conf, float(step_index), float(accum_failures)]])
        
        if self.is_trained:
            try:
                # Predict probability of the 'success' class (class 1)
                prob = self.calibrator.predict_proba(features)[0][1]
                return float(prob)
            except Exception as e:
                logger.warning(f"Error in Platt scaling model prediction: {e}. Falling back to default calibration.")
        
        # Fallback linear combination + sigmoid:
        z = np.dot(features[0], self.default_w) + self.default_b
        prob = 1.0 / (1.0 + np.exp(-z))
        return float(prob)

    def train_calibrator(self, X_train: List[List[float]], y_train: List[int]) -> bool:
        """
        Train the logistic calibrator on historical trajectory features.
        X_train: List of [self_conf, structural_conf, step_index, accum_failures]
        y_train: List of outcomes (1 for correct/success, 0 for incorrect/failure)
        """
        if len(X_train) < 5:
            logger.info("Confidence Estimator: Insufficient training data to train calibrator (need at least 5 samples).")
            return False
            
        # Check if we have both classes (0 and 1) in y_train
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
            logger.error(f"Confidence Estimator: Training error: {e}")
            return False
            
    def get_calibration_details(self) -> Dict[str, Any]:
        """Return model coefficients for transparency/explainability."""
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
