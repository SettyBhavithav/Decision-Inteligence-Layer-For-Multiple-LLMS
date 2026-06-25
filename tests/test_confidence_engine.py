import pytest
from decision_layer.confidence_engine.models import AgentConfidence
from decision_layer.confidence_engine.confidence_validator import ConfidenceValidator
from decision_layer.confidence_engine.confidence_calculator import RuleBasedConfidenceCalculator, BayesianConfidenceCalculator, ProposedConfidenceCalculator
from decision_layer.confidence_engine.confidence_engine import ConfidenceEngine

def test_confidence_validator():
    validator = ConfidenceValidator()
    assert validator.validate_confidence(0.90) is True
    assert validator.validate_confidence(-0.02) is False
    assert validator.validate_confidence(1.02) is False

def test_rule_based_calculator():
    calc = RuleBasedConfidenceCalculator(w_ver=0.4, w_qual=0.3, w_cov=0.3)
    res = calc.calculate({
        "verification_score": 0.90,
        "quality_score": 0.80,
        "evidence_coverage": 0.80
    })
    # 0.4 * 0.9 + 0.3 * 0.8 + 0.3 * 0.8 = 0.36 + 0.24 + 0.24 = 0.84
    assert res == pytest.approx(0.84)

def test_bayesian_calculator():
    calc = BayesianConfidenceCalculator(alpha_prior=4.0, beta_prior=1.0)
    res = calc.calculate({"verification_score": 0.95})
    # (4.0 + 0.95) / (4.0 + 1.0 + 1.0) = 4.95 / 6.0 = 0.825
    assert res == pytest.approx(0.825)

def test_proposed_calculator_claim_aware():
    calc = ProposedConfidenceCalculator()
    
    # Text with 2 claims
    metrics_claims = {
        "claims": [
            {"coverage": 0.90, "credibility": 0.90, "hallucination_risk": 0.0},
            {"coverage": 0.80, "credibility": 0.80, "hallucination_risk": 0.1}
        ],
        "critical_issues": 0
    }
    
    res = calc.calculate(metrics_claims)
    # Claim 1: 0.90 * 0.90 * 1.0 = 0.81
    # Claim 2: 0.80 * 0.80 * (0.9^2) = 0.64 * 0.81 = 0.5184
    # Avg: (0.81 + 0.5184) / 2 = 1.3284 / 2 = 0.6642
    assert res == pytest.approx(0.6642)

def test_proposed_calculator_critical_penalty():
    calc = ProposedConfidenceCalculator()
    
    metrics = {
        "claims": [
            {"coverage": 0.90, "credibility": 0.90, "hallucination_risk": 0.0}
        ],
        "critical_issues": 1  # Flags a penalty subtract of 0.25
    }
    
    res = calc.calculate(metrics)
    # Claim conf: 0.81. Penalty: 0.25. Result: 0.81 - 0.25 = 0.56
    assert res == pytest.approx(0.56)

def test_confidence_engine_orchestrator():
    engine = ConfidenceEngine(algorithm="proposed")
    
    initial = engine.store.get_confidence("research")
    assert initial.confidence_score == 0.85
    
    metrics = {
        "verification_score": 0.95,
        "quality_score": 0.90,
        "evidence_coverage": 0.95,
        "hallucination_risk": 0.01,
        "citation_accuracy": 0.99
    }
    res = engine.estimate_confidence("research", metrics)
    assert res["confidence"] > 0.0
    assert len(res["history"]) == 1
    assert res["history"][0]["agent_id"] == "research"
