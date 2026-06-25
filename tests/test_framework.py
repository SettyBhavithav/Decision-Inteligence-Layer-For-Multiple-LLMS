import os
import pytest
from agents.base_agent import AgentRegistry
from agents.research.research_agent import ResearchAgent
from agents.writing.writing_agent import WritingAgent
from agents.verification.verification_agent import VerificationAgent
from decision_layer.trust_engine.trust_engine import TrustEngine
from decision_layer.confidence_engine.confidence_estimator import ConfidenceEstimator
from decision_layer.decision_engine.decision_engine import DecisionEngine
from decision_layer.communication_manager.communication_manager import CommunicationManager
from decision_layer.failure_attribution.failure_attribution import FailureAttribution
from database.connection import DatabaseConnection
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory

@pytest.fixture
def db_conn():
    db_path = "test_metadata.db"
    conn = DatabaseConnection(db_path)
    yield conn
    # Cleanup database after tests
    if os.path.exists(db_path):
        conn.clear_database()
        try:
            os.remove(db_path)
        except PermissionError:
            pass

def test_agent_registry():
    registry = AgentRegistry()
    registry.clear()
    
    research = ResearchAgent()
    registry.register("research", research)
    
    assert "research" in registry.list_roles()
    assert registry.get_agent("research") == research

def test_trust_engine():
    engine = TrustEngine(initial_trust=0.5, eta_success=0.2, eta_failure=0.3)
    
    # Successful update
    new_score = engine.update_trust_on_success("research", w_contrib=1.0)
    assert new_score == 0.5 + 0.2 * (1.0 - 0.5) * 1.0  # 0.6
    assert engine.get_trust("research") == 0.6
    
    # Failure penalty
    engine.update_trust_on_failure("research", ["research", "writing"])
    # T_resp = 0.6 - 0.3 * 0.6 = 0.42
    assert pytest.approx(engine.get_trust("research")) == 0.42
    # Writing decay: T_j = 0.5 - 0.02 * 0.5 = 0.49
    assert pytest.approx(engine.get_trust("writing")) == 0.49

def test_confidence_estimator():
    estimator = ConfidenceEstimator()
    
    # Test structural confidence calculation
    score = estimator.estimate_structural_confidence(
        response="The Transformer is a deep learning model.", 
        reasoning="I am absolutely sure based on original literature."
    )
    assert score == 1.0
    
    # Test structural confidence with uncertainty word
    score_unc = estimator.estimate_structural_confidence(
        response="Maybe it works, but I am not sure.",
        reasoning="Uncertain response."
    )
    assert score_unc < 1.0
    
    # Default calibration
    calib_conf = estimator.calibrate(self_conf=0.8, structural_conf=0.9, step_index=1, accum_failures=0)
    assert 0.0 < calib_conf < 1.0

def test_decision_engine():
    engine = DecisionEngine(theta_accept=0.70, theta_verify=0.40)
    
    # High Trust + High Confidence -> ACCEPT
    res = engine.make_decision(trust_score=0.9, calibrated_conf=0.9, task_metadata={"complexity": "medium"})
    assert res["decision"] == "ACCEPT"
    
    # High Trust + Low Confidence -> VERIFY
    res_v = engine.make_decision(trust_score=0.8, calibrated_conf=0.5, task_metadata={"complexity": "medium"})
    assert res_v["decision"] == "VERIFY"
    
    # Low Trust + Low Confidence -> REJECT
    res_r = engine.make_decision(trust_score=0.3, calibrated_conf=0.3, task_metadata={"complexity": "medium"})
    assert res_r["decision"] == "REJECT"

def test_communication_manager():
    manager = CommunicationManager(bypass_enabled=True)
    
    # Verify bypass rule triggers
    should_r = manager.should_route(
        current_role="scheduler",
        next_role="citation",
        calibrated_conf=0.95,
        trust_score=0.95,
        task_metadata={"complexity": "low"}
    )
    # Should bypass (return False) because reliability 0.9025 > 0.88 and complexity is low
    assert should_r is False

def test_failure_attribution():
    attribution = FailureAttribution()
    
    trajectory = [
        {"role": "research", "simulated": True, "simulated_success": True},
        {"role": "writing", "simulated": True, "simulated_success": False},
        {"role": "citation", "simulated": True, "simulated_success": True}
    ]
    
    report = attribution.attribute_failure(trajectory, "Writing contains factual errors.", is_simulation=True)
    assert report["responsible_role"] == "writing"
    assert report["failure_step"] == 1

def test_memory_persistence(db_conn):
    short_term = ShortTermMemory(db_conn)
    long_term = LongTermMemory(db_conn)
    
    # Save active subtask
    short_term.save_subtask_state(
        task_id="task_0",
        conversation_id="session_123",
        description="Extract facts",
        role="research",
        status="ACCEPT",
        response="Factual output",
        confidence=0.9,
        calibrated_conf=0.85,
        trust=0.7
    )
    
    subtasks = short_term.get_subtask_responses("session_123")
    assert len(subtasks) == 1
    assert subtasks[0]["id"] == "task_0"
    
    # Save conversation
    long_term.save_conversation("session_123", "User query", "Framework output")
    with db_conn.get_connection() as conn:
        conn.row_factory = lambda cursor, row: {"id": row[0], "query": row[1], "response": row[2]}
        cursor = conn.cursor()
        conv = cursor.execute("SELECT * FROM conversations WHERE id = ?", ("session_123",)).fetchone()
    assert conv["id"] == "session_123"
    assert conv["query"] == "User query"
