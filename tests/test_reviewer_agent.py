import pytest
from agents.reviewer.models import ReviewIssue, QualityScore
from agents.reviewer.document_loader import DocumentLoader
from agents.reviewer.structure_reviewer import StructureReviewer
from agents.reviewer.consistency_reviewer import ConsistencyReviewer
from agents.reviewer.review_validator import ReviewValidator
from agents.reviewer.reviewer_agent import ReviewerAgent

def test_document_loader():
    loader = DocumentLoader()
    doc = loader.load_document({"draft": "Introduction content", "sections": []}, {"citations": []})
    assert doc["draft"] == "Introduction content"

def test_structure_reviewer_missing_headers():
    reviewer = StructureReviewer()
    issues = reviewer.review_structure("This is a simple text with no headings.")
    assert len(issues) > 0
    # Should flag missing mandatory headings (introduction, analysis, references)
    assert any("introduction" in issue.description.lower() for issue in issues)

def test_consistency_reviewer():
    reviewer = ConsistencyReviewer()
    issues = reviewer.review_consistency("This is a Multi-Agent system. It is a multiagent project.")
    assert len(issues) == 1
    assert "Acronym or term mismatch" in issues[0].description

def test_review_validator():
    validator = ReviewValidator(quality_threshold=0.85)
    
    # Approved case
    score_ok = QualityScore(structure_score=0.9, logic_score=0.9, evidence_score=0.9, citation_score=0.9, overall_quality=0.9)
    status_ok = validator.validate_review(score_ok, [])
    assert status_ok == "approved"
    
    # Revision needed case (below threshold)
    score_low = QualityScore(structure_score=0.7, logic_score=0.7, evidence_score=0.7, citation_score=0.7, overall_quality=0.7)
    status_low = validator.validate_review(score_low, [])
    assert status_low == "revision_needed"

def test_reviewer_agent_simulation():
    agent = ReviewerAgent()
    agent.use_simulation = True
    task = {"id": "task_review", "description": "Review final paper structure."}
    res = agent.execute(task, [])
    assert res["simulated"] is True
    assert "[Simulated Success]" in res["response"] or "[Simulated Error]" in res["response"]
