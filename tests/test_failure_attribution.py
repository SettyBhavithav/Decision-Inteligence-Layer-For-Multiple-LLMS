import pytest
from decision_layer.failure_attribution.models import FailurePackage
from decision_layer.failure_attribution.failure_detector import FailureDetector
from decision_layer.failure_attribution.root_cause_analyzer import RootCauseAnalyzer
from decision_layer.failure_attribution.failure_classifier import FailureClassifier
from decision_layer.failure_attribution.propagation_analyzer import FailurePropagationAnalyzer
from decision_layer.failure_attribution.recovery_planner import RecoveryPlanner
from decision_layer.failure_attribution.failure_validator import FailureValidator
from decision_layer.failure_attribution.failure_attribution import FailureAttribution

def test_failure_detector():
    detector = FailureDetector()
    
    # Factual verification below threshold
    assert detector.detect_failure({"verification_score": 0.70}) is True
    # Reviewer quality below threshold
    assert detector.detect_failure({"quality_score": 0.65}) is True
    # Hallucination risk above threshold
    assert detector.detect_failure({"hallucination_risk": 0.20}) is True
    # Normal metrics (no failure)
    assert detector.detect_failure({"verification_score": 0.90, "quality_score": 0.90, "hallucination_risk": 0.01}) is False

def test_root_cause_analyzer_confidence():
    analyzer = RootCauseAnalyzer()
    
    # Softmax confidence verification for Citation Failure
    rc = analyzer.analyze_root_cause("Citation Failure", {})
    assert rc.responsible_agent == "citation"
    assert rc.attribution_confidence > 0.50
    assert len(rc.alternative_candidates) > 0
    # Alternates should have confidences associated
    assert rc.alternative_candidates[0]["agent"] == "research"

def test_failure_classifier():
    classifier = FailureClassifier()
    
    assert classifier.classify_failure({"error": "Failed to resolve DOI citation"}) == "Citation Failure"
    assert classifier.classify_failure({"hallucination_risk": 0.25}) == "Hallucination"
    assert classifier.classify_failure({"verification_score": 0.50}) == "Verification Failure"

def test_propagation_analyzer():
    analyzer = FailurePropagationAnalyzer()
    agents = ["planner", "research", "writing", "reviewer"]
    
    path = analyzer.trace_propagation("writing", agents)
    assert path == ["writing", "reviewer"]

def test_recovery_planner():
    planner = RecoveryPlanner()
    
    plan1 = planner.plan_recovery("Citation Failure", "citation", {"attempts": 1})
    assert plan1.recommended_action == "RETRY"
    
    plan2 = planner.plan_recovery("Hallucination", "writing", {"attempts": 1})
    assert plan2.recommended_action == "REGENERATE"
    
    # Escalate on maximum attempts exceeded
    plan3 = planner.plan_recovery("Hallucination", "writing", {"attempts": 3, "max_attempts": 3})
    assert plan3.recommended_action == "ESCALATE"

def test_failure_validator():
    validator = FailureValidator()
    # Validator checks validity of recovery plans
    assert validator.allowed_actions == {"RETRY", "REGENERATE", "ESCALATE", "REJECT", "CONTINUE"}

def test_failure_attribution_orchestrator():
    attribution = FailureAttribution()
    
    active_agents = ["planner", "research", "writing", "reviewer"]
    metrics = {
        "verification_score": 0.70, # Failure trigger
        "hallucination_risk": 0.20,
        "attempts": 1
    }
    
    res = attribution.run_attribution("w_303", active_agents, metrics)
    assert res["failure_detected"] is True
    assert res["responsible_agent"] == "research"
    assert res["recovery_plan"]["recommended_action"] in ["RETRY", "REGENERATE", "REJECT"]
