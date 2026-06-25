import pytest
from agents.citation.models import CitationPlaceholder, BibliographyEntry
from agents.citation.placeholder_extractor import PlaceholderExtractor
from agents.citation.reference_matcher import ReferenceMatcher
from agents.citation.doi_validator import DOIValidator
from agents.citation.duplicate_checker import DuplicateCitationChecker
from agents.citation.citation_formatter import CitationFormatter
from agents.citation.bibliography_generator import BibliographyGenerator
from agents.citation.citation_agent import CitationAgent

def test_placeholder_extractor():
    extractor = PlaceholderExtractor()
    draft = "Wei et al. proposes CoT [CITATION_01], and Wang et al. builds self-consistency [CITATION_02]."
    keys = extractor.extract_placeholders(draft)
    assert len(keys) == 2
    assert keys[0] == "[CITATION_01]"
    assert keys[1] == "[CITATION_02]"

def test_reference_matcher():
    matcher = ReferenceMatcher()
    keys = ["[CITATION_01]", "[CITATION_02]"]
    placeholders_map = [
        {"key": "[CITATION_01]", "source_id": "paper_01"},
        {"key": "[CITATION_02]", "source_id": "paper_02"}
    ]
    resolved = matcher.match_references(keys, placeholders_map, [])
    assert len(resolved) == 2
    assert resolved[0].matched_source_id == "paper_01"

def test_doi_validator():
    validator = DOIValidator()
    
    val_1 = validator.validate_doi("10.1145/3318464.3389700")
    assert val_1["status"] == "valid"
    
    val_2 = validator.validate_doi("invalid_doi_format")
    assert val_2["status"] == "invalid"

def test_duplicate_citation_checker():
    checker = DuplicateCitationChecker()
    refs = [
        {"id": "paper_01", "doi": "10.1234/test"},
        {"id": "paper_01", "doi": "10.1234/test"}
    ]
    clean = checker.remove_duplicates(refs)
    assert len(clean) == 1
    assert checker.duplicate_count == 1

def test_citation_formatter():
    formatter = CitationFormatter()
    paper = {
        "title": "Chain of Thought",
        "authors": "Wei et al.",
        "venue": "NeurIPS",
        "year": 2022,
        "doi": "10.1234/cot"
    }
    
    formatted_ieee = formatter.format_citation(paper, 1, "IEEE")
    assert '[1] Wei et al., "Chain of Thought," *NeurIPS*, 2022.' in formatted_ieee
    
    formatted_apa = formatter.format_citation(paper, 1, "APA")
    assert 'Wei et al. (2022). Chain of Thought. *NeurIPS*.' in formatted_apa

def test_citation_agent_simulation():
    agent = CitationAgent()
    agent.use_simulation = True
    
    task = {"id": "task_cite", "description": "Resolve citation placeholders."}
    res = agent.execute(task, [])
    assert res["simulated"] is True
    assert "[Simulated Success]" in res["response"] or "[Simulated Error]" in res["response"]
