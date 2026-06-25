import pytest
from decision_layer.decision_engine.models import DecisionInput
from decision_layer.decision_engine.decision_validator import DecisionValidator
from decision_layer.decision_engine.decision_calculator import RuleBasedDecisionCalculator, WeightedDecisionCalculator, ProposedDecisionCalculator
from decision_layer.decision_engine.decision_engine import DecisionEngine

def test_decision_validator():
    validator = DecisionValidator()
    assert validator.validate_decision("ACCEPT", {"trust_score": 0.8, "confidence_score": 0.8}) is True
    assert validator.validate_decision("UNKNOWN", {"trust_score": 0.8, "confidence_score": 0.8}) is False
    assert validator.validate_decision("ACCEPT", {"trust_score": 0.8}) is False

def test_rule_based_calculator():
    calc = RuleBasedDecisionCalculator()
    
    # High trust/confidence -> ACCEPT
    res1 = calc.calculate_decision({"trust_score": 0.90, "confidence_score": 0.95})
    assert res1 == "ACCEPT"
    
    # Low trust/confidence -> REGENERATE
    res2 = calc.calculate_decision({"trust_score": 0.50, "confidence_score": 0.85})
    assert res2 == "REGENERATE"
    
    # Medium values -> VERIFY
    res3 = calc.calculate_decision({"trust_score": 0.70, "confidence_score": 0.70})
    assert res3 == "VERIFY"

def test_weighted_calculator():
    calc = WeightedDecisionCalculator(w_t=0.2, w_c=0.3, w_v=0.3, w_q=0.2)
    
    # High score -> ACCEPT
    res1 = calc.calculate_decision({
        "trust_score": 0.90, "confidence_score": 0.90, "verification_score": 0.90, "quality_score": 0.90
    })
    assert res1 == "ACCEPT"
    
    # Medium score -> VERIFY
    res2 = calc.calculate_decision({
        "trust_score": 0.70, "confidence_score": 0.70, "verification_score": 0.70, "quality_score": 0.70
    })
    assert res2 == "VERIFY"
    
    # Low score -> REGENERATE
    res3 = calc.calculate_decision({
        "trust_score": 0.50, "confidence_score": 0.50, "verification_score": 0.50, "quality_score": 0.50
    })
    assert res3 == "REGENERATE"

def test_proposed_calculator_adaptive():
    calc = ProposedDecisionCalculator()
    
    # High utility -> ACCEPT
    res1 = calc.calculate_decision({
        "trust_score": 0.90, "confidence_score": 0.90, "hallucination_risk": 0.0
    })
    # 0.9 * 0.9 = 0.81 >= 0.75 -> ACCEPT
    assert res1 == "ACCEPT"
    
    # High risk -> VERIFY
    res2 = calc.calculate_decision({
        "trust_score": 0.90, "confidence_score": 0.90, "hallucination_risk": 0.15
    })
    assert res2 == "VERIFY"
    
    # Very high risk -> REGENERATE
    res3 = calc.calculate_decision({
        "trust_score": 0.90, "confidence_score": 0.90, "hallucination_risk": 0.40
    })
    assert res3 == "REGENERATE"

def test_decision_engine_orchestrator():
    engine = DecisionEngine(algorithm="proposed")
    
    inputs = {
        "trust_score": 0.90,
        "confidence_score": 0.90,
        "verification_score": 0.95,
        "quality_score": 0.95,
        "hallucination_risk": 0.0,
        "evidence_coverage": 0.95
    }
    
    res = engine.evaluate_decision("w_999", inputs)
    assert res["decision"] == "ACCEPT"
    assert len(res["history"]) == 1
    assert res["history"][0]["decision"] == "ACCEPT"
