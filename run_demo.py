import logging
import json
from workflows.graph import FrameworkOrchestrator

# Setup basic logging to console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_pipeline_demo():
    print("==============================================================")
    # 1. Initialize Orchestrator in Simulation Mode
    print("Initializing Trust-Aware Dynamic Collaboration Framework...")
    orchestrator = FrameworkOrchestrator(use_simulation=True, db_path="demo_metadata.db")
    
    # Clean database for clean demo run
    orchestrator.db_conn.clear_database()
    
    # Configure mock agent capabilities for evaluation
    agent_skills = {
        "research": 0.85,
        "writing": 0.70,     # Let's make writing agent fail more to see retry/failure updates
        "citation": 0.90,
        "reviewer": 0.75,
        "verification": 0.95
    }
    for role, skill in agent_skills.items():
        agent = orchestrator.registry.get_agent(role)
        if agent:
            agent.true_success_rate = skill
            
    print("Framework initialized with Specialized Agents.")
    print("Simulation mode active (No real LLM API token charges).")
    print("==============================================================\n")
    
    # 2. Run Task Query
    query = "Create a literature review summarizing the impact of self-consistency on chain of thought."
    print(f"Submitting query: '{query}'\n")
    
    run_res = orchestrator.run_task(query, complexity="medium")
    
    # 3. Print Results
    result = run_res["result"]
    trajectory = run_res["trajectory"]
    metrics = run_res["metrics"]
    
    print("\n================== INTERMEDIATE WORKFLOW TRACE ==================")
    for step in trajectory:
        print(f"Step {step['step']}: Role={step['role'].upper()} (Agent={step['agent_name']})")
        print(f"  Task Description: {step['task_description']}")
        print(f"  Confidence: Raw={step['raw_confidence']:.2f} | Calibrated={step['calibrated_conf']:.2f}")
        print(f"  Trust Score: {step['trust_score']:.2f}")
        print(f"  Decision Outcome: {step['decision']}")
        print(f"  Reasoning snippet: {step['reasoning']}")
        print("-" * 50)
        
    print("\n================== FINAL RESPONSE OUTPUT ==================")
    print(result.get("response"))
    print("===========================================================")
    
    print("\n================== PERFORMANCE METRICS ==================")
    print(f"Overall Status: {result.get('status').upper()}")
    print(f"Average Calibrated Confidence: {result.get('average_confidence'):.3f}")
    print(f"Total Execution Steps: {result.get('trajectory_steps')}")
    print(f"Execution Latency: {metrics['latencies'].get('total_execution', 0.0):.3f}s")
    print(f"Total Tokens Consumed: {metrics['token_usage']['total']}")
    
    print("\nFinal Agent Trust Scores:")
    for role, score in result.get("agent_trust_scores").items():
        print(f"  - {role.capitalize()}: {score:.3f}")
    print("===========================================================")

if __name__ == "__main__":
    run_pipeline_demo()

# built citation verification agent to cross-check factual claims

# added voting consensus logic between multiple LLM agents

# created project layout for multi-agent LLM decision layer

# searched arXiv API for claim verification source links

# calculated trust score from 0 to 1 based on source validation

# created base agent abstract class and AgentState model

# created dynamic router picking best LLM based on prompt difficulty

# created demo script running sample multi-agent research workflow

# built citation verification agent to cross-check factual claims

# added voting consensus logic between multiple LLM agents

# created project layout for multi-agent LLM decision layer

# searched arXiv API for claim verification source links

# calculated trust score from 0 to 1 based on source validation

# created base agent abstract class and AgentState model

# created dynamic router picking best LLM based on prompt difficulty

# created demo script running sample multi-agent research workflow

# built citation verification agent to cross-check factual claims

# added voting consensus logic between multiple LLM agents

# created project layout for multi-agent LLM decision layer

# searched arXiv API for claim verification source links

# calculated trust score from 0 to 1 based on source validation

# created base agent abstract class and AgentState model

# created dynamic router picking best LLM based on prompt difficulty

# created demo script running sample multi-agent research workflow

# built citation verification agent to cross-check factual claims

# added voting consensus logic between multiple LLM agents

# built citation verification agent to cross-check factual claims

# added voting consensus logic between multiple LLM agents

# created project layout for multi-agent LLM decision layer

# searched arXiv API for claim verification source links

# calculated trust score from 0 to 1 based on source validation

# created base agent abstract class and AgentState model

# created dynamic router picking best LLM based on prompt difficulty

# created demo script running sample multi-agent research workflow

# built citation verification agent to cross-check factual claims
