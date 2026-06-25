import pytest
from decision_layer.trust_engine.models import AgentTrust
from decision_layer.trust_engine.trust_validator import TrustValidator
from decision_layer.trust_engine.trust_calculator import RuleBasedTrustCalculator, BayesianTrustCalculator, ProposedTrustCalculator
from decision_layer.trust_engine.trust_engine import TrustEngine

def test_trust_validator():
    validator = TrustValidator()
    assert validator.validate_trust(0.85) is True
    assert validator.validate_trust(-0.01) is False
    assert validator.validate_trust(1.05) is False

def test_rule_based_calculator():
    calc = RuleBasedTrustCalculator(increment=0.05, penalty=0.10)
    
    # Success increment
    t1 = calc.calculate(0.80, {"success": True})
    assert t1 == pytest.approx(0.85)
    
    # Failure penalty
    t2 = calc.calculate(0.80, {"success": False})
    assert t2 == pytest.approx(0.70)

def test_bayesian_calculator():
    calc = BayesianTrustCalculator()
    
    # Success updates expectation upwards
    t1 = calc.calculate(0.80, {"verification_score": 0.9, "quality_score": 0.9, "success": True})
    assert t1 > 0.80
    
    # Failure updates expectation downwards
    t2 = calc.calculate(0.80, {"verification_score": 0.2, "quality_score": 0.2, "success": False})
    assert t2 < 0.80

def test_proposed_calculator_hallucination_penalty():
    calc = ProposedTrustCalculator(learning_rate=0.2, w_verification=0.6, w_quality=0.4, w_risk=0.2)
    
    # Normal success
    t_normal = calc.calculate(0.80, {"verification_score": 0.9, "quality_score": 0.9, "hallucination_risk": 0.0})
    
    # Success but with high hallucination risk (penalty scales quadratically)
    t_risk = calc.calculate(0.80, {"verification_score": 0.9, "quality_score": 0.9, "hallucination_risk": 0.8})
    
    assert t_risk < t_normal

def test_trust_engine_orchestrator():
    # Since we are testing offline/without NIM keys, we verify the engine can initialize and run proposed updates
    engine = TrustEngine(algorithm="proposed")
    
    # Initialize store checks
    initial = engine.store.get_trust("research")
    assert initial.trust_score == 0.80
    
    # Update simulation
    metrics = {"verification_score": 0.95, "quality_score": 0.90, "hallucination_risk": 0.01, "success": True}
    res = engine.update_trust("research", metrics)
    
    assert res["trust_score"] > 0.80
    assert len(res["history"]) == 1
    assert res["history"][0]["agent_id"] == "research"
