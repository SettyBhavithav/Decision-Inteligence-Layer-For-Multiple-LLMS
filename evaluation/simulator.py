import logging
from typing import Dict, Any, List
from workflows.graph import FrameworkOrchestrator

logger = logging.getLogger("trust_framework")

class SimulationSuite:
    """
    Simulation & Batch Evaluation Suite (Layer 10).
    Runs batch simulated workloads with parameterizable agent skill rates
    to statistically analyze trust learning, calibration, and routing efficiency.
    """
    def __init__(self, db_path: str = "simulation_metadata.db"):
        self.db_path = db_path
        self.orchestrator = None

    def run_simulation_batch(self, 
                             num_runs: int = 10, 
                             agent_skills: Dict[str, float] = None, 
                             agent_biases: Dict[str, float] = None,
                             complexity: str = "medium",
                             bypass_comm: bool = True,
                             static_trust: bool = False,
                             calibration: bool = True,
                             use_fae: bool = True,
                             no_decision: bool = False) -> Dict[str, Any]:
        """
        Runs a batch of simulated query workloads.
        """
        # Persistent orchestrator to allow trust score learning to carry over between sequential runs (Modification 2 & 3)
        if self.orchestrator is None:
            self.orchestrator = FrameworkOrchestrator(use_simulation=True, db_path=self.db_path)
            self.orchestrator.db_conn.clear_database()
        else:
            self.orchestrator.comm_manager.reset()
            
        orchestrator = self.orchestrator
        
        # Configure modular DILS flags
        orchestrator.static_trust = static_trust
        orchestrator.use_calibration = calibration
        orchestrator.use_fae = use_fae
        orchestrator.no_decision = no_decision
        
        # Override agent parameters if specified
        if agent_skills:
            for role, skill in agent_skills.items():
                agent = orchestrator.registry.get_agent(role)
                if agent:
                    agent.true_success_rate = skill
                    
        if agent_biases:
            for role, bias in agent_biases.items():
                agent = orchestrator.registry.get_agent(role)
                if agent:
                    agent.calibration_bias = bias

        # Generalized Fault Injection Mechanism (Modification 2)
        import random
        degraded_role = random.choice(["research", "writing", "citation", "reviewer", "verification"])
        fail_start = random.randint(2, max(2, num_runs - 5))
        fail_duration = random.randint(2, 4)
        fail_end = fail_start + fail_duration
        degradation_mode = random.choice(["low_success", "high_hallucination", "high_error", "delay"])

        orig_skills = {}
        orig_biases = {}
        for r in ["research", "writing", "citation", "reviewer", "verification"]:
            ag = orchestrator.registry.get_agent(r)
            if ag:
                orig_skills[r] = ag.true_success_rate
                orig_biases[r] = ag.calibration_bias

        # Batch records
        success_count = 0
        total_tokens = 0
        total_latency = 0.0
        total_steps = 0
        
        final_trust_scores: List[Dict[str, float]] = []
        all_attributions = []
        all_degraded_runs = []
        run_records = []

        logger.info(f"Simulation: Running batch of {num_runs} simulated tasks...")

        for i in range(num_runs):
            # Apply generalized degradation if within failure window
            is_currently_degraded = False
            if fail_start <= i < fail_end:
                ag = orchestrator.registry.get_agent(degraded_role)
                if ag:
                    is_currently_degraded = True
                    if degradation_mode == "low_success":
                        ag.true_success_rate = 0.15
                    elif degradation_mode == "high_hallucination":
                        ag.true_success_rate = 0.20
                        ag.calibration_bias = 0.35
                    elif degradation_mode == "high_error":
                        ag.true_success_rate = 0.10
                    elif degradation_mode == "delay":
                        import time
                        time.sleep(0.01)
                all_degraded_runs.append(i)
            else:
                # Restore original skills
                for r in ["research", "writing", "citation", "reviewer", "verification"]:
                    ag = orchestrator.registry.get_agent(r)
                    if ag:
                        ag.true_success_rate = orig_skills.get(r, 0.80)
                        ag.calibration_bias = orig_biases.get(r, 0.0)

            query = f"Simulated test query number {i+1}"
            run_res = orchestrator.run_task(query, complexity=complexity, bypass_comm=bypass_comm)
            
            # Record stats (Trajectory correctness verification)
            result = run_res["result"]
            trajectory = run_res.get("trajectory", [])
            
            run_succeeded = (result.get("status") == "success")
            if run_succeeded:
                task_steps = {}
                for step in trajectory:
                    tid = step.get("task_id")
                    if tid:
                        task_steps[tid] = step
                
                for tid, final_step in task_steps.items():
                    if final_step.get("decision") == "ACCEPT" and not final_step.get("simulated_success", True):
                        run_succeeded = False
                        break
            
            if run_succeeded:
                success_count += 1
                
            metrics = run_res["metrics"]
            total_tokens += metrics["token_usage"]["total"]
            total_latency += metrics["latencies"].get("total_execution", 0.0)
            total_steps += result.get("trajectory_steps", 0)
            
            # Record attributions of this run
            run_attributions = run_res.get("attributions", [])
            for attr in run_attributions:
                attr["ground_truth_culprit"] = degraded_role if is_currently_degraded else ""
                all_attributions.append(attr)
            
            final_trust_scores.append(orchestrator.trust_engine.get_all_trust_scores())
            
            # Append run record (Modification 3 & 4)
            run_records.append({
                "success": run_succeeded,
                "tokens": metrics["token_usage"]["total"],
                "latency": metrics["latencies"].get("total_execution", 0.0),
                "steps": result.get("trajectory_steps", 0),
                "attributions": [dict(a) for a in run_attributions],
                "trust_scores": orchestrator.trust_engine.get_all_trust_scores(),
                "communication_metrics": orchestrator.comm_manager.get_metrics(),
            })

        # Compile final stats
        avg_ece = orchestrator.logger_layer.calculate_ece()
        avg_brier = orchestrator.logger_layer.calculate_brier_score()
        success_rate = success_count / num_runs
        
        # Aggregate final trust scores
        aggregated_trust = {}
        for role in orchestrator.registry.list_roles():
            scores = [run_scores.get(role, 0.5) for run_scores in final_trust_scores]
            aggregated_trust[role] = float(sum(scores) / len(scores))

        summary = {
            "num_runs": num_runs,
            "success_rate": success_rate,
            "average_ece": avg_ece,
            "average_brier_score": avg_brier,
            "average_latency_seconds": total_latency / num_runs,
            "average_tokens_consumed": total_tokens / num_runs,
            "average_steps_per_run": total_steps / num_runs,
            "communication_metrics": orchestrator.comm_manager.get_metrics(),
            "final_trust_scores": aggregated_trust,
            "degraded_agent": degraded_role,
            "degraded_runs": all_degraded_runs,
            "attributions": all_attributions,
            "runs": run_records
        }
        
        logger.info(f"Simulation Batch Finished. Success Rate: {success_rate:.2%}, ECE: {avg_ece:.3f}, Brier: {avg_brier:.3f}")
        return summary
