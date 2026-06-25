"""
scalability_runner.py — Measures framework performance under increasing complexity.
Sweeps: num_agents, workflow_depth, token_budget.
"""
import logging
import numpy as np
from typing import Dict, Any, List
from evaluation.benchmark_runner import BenchmarkRunner, PROPOSED
from experiments.experiment_config import (SKILLS_MEDIUM, BIASES_DEFAULT,
                                           SCALABILITY_NUM_AGENTS,
                                           SCALABILITY_WORKFLOW_DEPTH,
                                           SCALABILITY_TOKEN_BUDGETS,
                                           SCALABILITY_RUNS)

logger = logging.getLogger("trust_framework")


def _run_scaled(num_agents: int, depth: int, token_budget: int, runs: int) -> Dict[str, float]:
    """
    Simulate scaled conditions by adjusting skill profiles as a proxy for complexity.
    Higher agent count → slightly lower per-agent skill (coordination overhead proxy).
    Higher token budget → better quality proxy.
    """
    np.random.seed(3)
    # Coordination overhead: skill degrades slightly with more agents
    overhead = max(0.0, (num_agents - 5) * 0.03)
    budget_bonus = min(0.05, (token_budget - 1000) / 1000 * 0.01)
    depth_penalty = max(0.0, (depth - 4) * 0.02)

    skills = {k: min(0.99, max(0.20, v - overhead + budget_bonus - depth_penalty))
              for k, v in SKILLS_MEDIUM.items()}

    runner = BenchmarkRunner()
    results = runner.run_all(num_runs=runs, agent_skills=skills, agent_biases=BIASES_DEFAULT)
    proposed = results[PROPOSED]
    return {
        "success_rate":          proposed["task"]["success_rate"],
        "average_e2e_latency_s": proposed["system"]["average_e2e_latency_s"],
        "total_tokens":          proposed["system"]["total_tokens_consumed"],
        "throughput":            proposed["system"]["throughput_runs_per_second"],
    }


def run_scalability_experiments(runs: int = SCALABILITY_RUNS) -> Dict[str, Any]:
    logger.info("ScalabilityRunner: Starting scalability sweeps")
    results: Dict[str, Any] = {
        "num_agents":    {},
        "workflow_depth":{},
        "token_budget":  {},
    }

    # Sweep num_agents (depth=4, budget=1000 fixed)
    for n in SCALABILITY_NUM_AGENTS:
        m = _run_scaled(num_agents=n, depth=4, token_budget=1000, runs=runs)
        results["num_agents"][n] = m
        logger.info(f"ScalabilityRunner [agents={n}]: latency={m['average_e2e_latency_s']:.3f}s")

    # Sweep workflow_depth (agents=5, budget=1000 fixed)
    for d in SCALABILITY_WORKFLOW_DEPTH:
        m = _run_scaled(num_agents=5, depth=d, token_budget=1000, runs=runs)
        results["workflow_depth"][d] = m
        logger.info(f"ScalabilityRunner [depth={d}]: latency={m['average_e2e_latency_s']:.3f}s")

    # Sweep token_budget (agents=5, depth=4 fixed)
    for b in SCALABILITY_TOKEN_BUDGETS:
        m = _run_scaled(num_agents=5, depth=4, token_budget=b, runs=runs)
        results["token_budget"][b] = m
        logger.info(f"ScalabilityRunner [budget={b}]: success={m['success_rate']:.3f}")

    return results
