import pytest
from agents.writing.models import Section, Placeholder
from agents.writing.context_loader import ContextLoader
from agents.writing.outline_generator import OutlineGenerator
from agents.writing.section_planner import SectionPlanner
from agents.writing.style_formatter import StyleFormatter
from agents.writing.citation_placeholder import CitationPlaceholderManager
from agents.writing.writing_agent import WritingAgent

def test_context_loader_ingestion():
    loader = ContextLoader()
    raw_evidence = {
        "summary": "CoT enables multi-step reasoning.",
        "evidence": [{"id": "paper_01", "content": "CoT math details"}],
        "workflow_id": "test_wf",
        "task_id": "task_1"
    }
    context = loader.load_context(raw_evidence)
    assert context["workflow_id"] == "test_wf"
    assert len(context["evidence"]) == 1

def test_outline_generator_model():
    generator = OutlineGenerator()
    assert generator.model == "stepfun-ai/step-3.7-flash"

def test_section_planner():
    planner = SectionPlanner()
    section = Section(
        title="Literature Review",
        goal="Summarize related work",
        required_evidence=["paper_01"],
        target_length=150
    )
    mock_evidence = [
        {"id": "paper_01", "content": "Wei et al. details"},
        {"id": "paper_02", "content": "Wang et al. details"}
    ]
    plan = planner.plan_section(section, mock_evidence)
    assert len(plan["evidence"]) == 1
    assert plan["evidence"][0]["id"] == "paper_01"

def test_style_formatter():
    formatter = StyleFormatter()
    raw_text = "This is a section."
    
    formatted_executive = formatter.format_style(raw_text, "executive")
    assert "## Executive Summary" in formatted_executive
    
    formatted_ieee = formatter.format_style(raw_text, "ieee")
    assert "# TECHNICAL RESEARCH REPORT" in formatted_ieee

def test_citation_placeholder_substitution():
    manager = CitationPlaceholderManager()
    raw_draft = (
        "Chain of Thought enables deep reasoning [[CITATION:paper_01]]. "
        "Self-consistency samples multiple paths [[CITATION:paper_02]]. "
        "Another check validates CoT [[CITATION:paper_01]]."
    )
    
    replaced, placeholders = manager.manage_placeholders(raw_draft)
    
    # Matches must be replaced with CITATION_01 and CITATION_02
    assert "[CITATION_01]" in replaced
    assert "[CITATION_02]" in replaced
    assert "[[CITATION:paper_01]]" not in replaced
    assert len(placeholders) == 2
    assert placeholders[0].key == "[CITATION_01]"
    assert placeholders[0].source_id == "paper_01"

def test_writing_agent_simulation():
    agent = WritingAgent()
    agent.use_simulation = True
    
    task = {"id": "task_write", "description": "Draft literature review."}
    res = agent.execute(task, [])
    assert res["simulated"] is True
    assert "[Simulated Success]" in res["response"] or "[Simulated Error]" in res["response"]
