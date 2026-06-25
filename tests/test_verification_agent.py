import pytest
from agents.verification.models import ClaimRecord, VerificationScore, VerificationIssue
from agents.verification.evidence_matcher import EvidenceMatcher
from agents.verification.citation_verifier import CitationVerifier
from agents.verification.consistency_verifier import ConsistencyVerifier
from agents.verification.verification_validator import VerificationValidator
from agents.verification.verification_agent import VerificationAgent

def test_evidence_matcher():
    matcher = EvidenceMatcher()
    claims = [ClaimRecord(claim_id=1, claim="Token savings of 28%.", paragraph=1)]
    provenance = [{"claim": "Savings of 28%.", "supported_by": ["paper_02"]}]
    
    matches = matcher.match_evidence(claims, provenance)
    assert len(matches) == 1
    assert matches[0].supporting_sources == ["paper_02"]

def test_citation_verifier_missing_entry():
    verifier = CitationVerifier()
    text = "Recent work shows significant results [1], and CoT improves reasoning [2]."
    bibliography = [{"key": "[1]", "formatted_reference": "Wei et al. reference"}]
    
    issues = verifier.verify_citations(text, bibliography)
    assert len(issues) == 1
    assert "has no matching reference entry" in issues[0].description

def test_consistency_verifier():
    verifier = ConsistencyVerifier()
    issues = verifier.verify_consistency("We build the proposed framework. The proposed system performs well.")
    assert len(issues) == 1
    assert "proposed framework" in issues[0].description

def test_verification_validator():
    validator = VerificationValidator(accuracy_threshold=0.85, hallucination_threshold=0.15)
    
    # Valid case
    score_ok = VerificationScore(claim_accuracy=0.9, citation_accuracy=0.9, evidence_coverage=0.9, hallucination_risk=0.05, overall_verification=0.9)
    assert validator.validate_verification(score_ok, []) is True
    
    # Invalid case (critical issue)
    issues = [VerificationIssue(description="Factual error", severity="critical")]
    assert validator.validate_verification(score_ok, issues) is False

def test_verification_agent_simulation():
    agent = VerificationAgent()
    agent.use_simulation = True
    task = {"id": "task_verify", "description": "Verify empirical calculations."}
    res = agent.execute(task, [])
    assert res["simulated"] is True
    assert "[Simulated Success]" in res["response"] or "[Simulated Error]" in res["response"]
