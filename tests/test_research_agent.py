import pytest
from agents.research.models import RetrievedDocument, ProvenanceRecord
from agents.research.query_understanding import QueryUnderstanding
from agents.research.retrieval_manager import RetrievalManager
from agents.research.source_manager import SourceManager
from agents.research.evidence_ranker import EvidenceRanker
from agents.research.duplicate_removal import DuplicateRemoval
from agents.research.provenance_generator import ProvenanceGenerator
from agents.research.research_agent import ResearchAgent

def test_query_understanding_model():
    analyzer = QueryUnderstanding()
    assert analyzer.model == "deepseek-ai/deepseek-v4-flash"

def test_retrieval_manager_retrieve():
    manager = RetrievalManager()
    docs = manager.retrieve({"keywords": ["prompting", "chain"]})
    assert len(docs) > 0
    assert any("chain" in doc.title.lower() or "prompting" in doc.title.lower() for doc in docs)

def test_source_manager_normalize():
    manager = SourceManager()
    dirty_docs = [
        RetrievedDocument(
            id="doc_1",
            title="   Test Title   ",
            content="Some research content",
            doi="10.1234/test.doi",
            url="https://test.url"
        )
    ]
    normalized = manager.normalize_sources(dirty_docs)
    assert normalized[0].title == "Test Title"

def test_evidence_ranker():
    ranker = EvidenceRanker(w_semantic=0.5, w_credibility=0.3, w_recency=0.2)
    docs = [
        RetrievedDocument(id="doc_old", title="Old Paper", content="Old", score=0.6, credibility_score=0.8, year=2010),
        RetrievedDocument(id="doc_new", title="New Paper", content="New", score=0.6, credibility_score=0.8, year=2025)
    ]
    ranked = ranker.rank(docs)
    # The newer paper must have higher ranking score and appear first
    assert ranked[0].id == "doc_new"

def test_duplicate_removal():
    dedup = DuplicateRemoval(jaccard_threshold=0.7)
    docs = [
        RetrievedDocument(id="doc_1", title="Original", content="this is a unique and original research content sentence block", score=0.5),
        RetrievedDocument(id="doc_2", title="Duplicate", content="this is a unique and original research content sentence block", score=0.5)
    ]
    unique = dedup.remove_duplicates(docs)
    assert len(unique) == 1
    assert dedup.removed_count == 1

def test_provenance_generator_model():
    prov = ProvenanceGenerator()
    assert prov.model == "deepseek-ai/deepseek-v4-flash"

def test_research_agent_simulation():
    agent = ResearchAgent()
    agent.use_simulation = True
    
    task = {"id": "task_research", "description": "Review model calibration problems."}
    res = agent.execute(task, [])
    assert res["simulated"] is True
    assert "[Simulated Success]" in res["response"] or "[Simulated Error]" in res["response"]
