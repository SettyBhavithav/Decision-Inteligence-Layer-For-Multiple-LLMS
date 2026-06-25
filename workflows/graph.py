import uuid
import logging
from typing import Dict, Any, List

# Core Agent Imports
from agents.planner.planner_agent import PlannerAgent
from agents.scheduler.scheduler_agent import DynamicTaskScheduler
from agents.base_agent import AgentRegistry
from agents.research.research_agent import ResearchAgent
from agents.writing.writing_agent import WritingAgent
from agents.citation.citation_agent import CitationAgent
from agents.reviewer.reviewer_agent import ReviewerAgent
from agents.verification.verification_agent import VerificationAgent

# Research Layer Imports (DIL)
from decision_layer.trust_engine.trust_engine import TrustEngine
from decision_layer.confidence_engine.confidence_estimator import ConfidenceEstimator
from decision_layer.decision_engine.decision_engine import DecisionEngine
from decision_layer.communication_manager.communication_manager import CommunicationManager
from decision_layer.failure_attribution.failure_attribution import FailureAttribution

# Memory & Persistence Imports
from database.connection import DatabaseConnection
from memory.short_term import ShortTermMemory
from memory.long_term import LongTermMemory
from memory.aggregator import ResponseAggregator
from evaluation.metrics import EventLogger

logger = logging.getLogger("trust_framework")

class FrameworkOrchestrator:
    """
    Framework Orchestrator.
    Implements the complete end-to-end execution flow defined in Phase 10 WSMS.
    """
    def __init__(self, use_simulation: bool = False, db_path: str = "metadata.db"):
        self.use_simulation = use_simulation
        
        # Initialize databases and memories
        self.db_conn = DatabaseConnection(db_path)
        self.short_term_memory = ShortTermMemory(self.db_conn)
        self.long_term_memory = LongTermMemory(self.db_conn)
        
        # Pluggable DILS configuration flags (Phase 3 Gating)
        self.static_trust = False
        self.use_calibration = True
        self.use_fae = True
        self.no_decision = False
        
        # Initialize DIL components
        self.planner = PlannerAgent()
        self.planner.use_simulation = use_simulation
        
        self.trust_engine = TrustEngine()
        self.confidence_estimator = ConfidenceEstimator()
        self.decision_engine = DecisionEngine()
        self.comm_manager = CommunicationManager()
        self.failure_attribution = FailureAttribution()
        self.aggregator = ResponseAggregator()
        self.aggregator.use_simulation = use_simulation
        self.logger_layer = EventLogger()
        
        # Register specialized agents
        self.registry = AgentRegistry()
        self.registry.clear()
        self.registry.register("research", ResearchAgent())
        self.registry.register("writing", WritingAgent())
        self.registry.register("citation", CitationAgent())
        self.registry.register("reviewer", ReviewerAgent())
        self.registry.register("verification", VerificationAgent())
        
        # Configure simulation settings
        if self.use_simulation:
            for role in self.registry.list_roles():
                agent = self.registry.get_agent(role)
                if agent:
                    agent.use_simulation = True

    def run_task(self, query: str, complexity: str = "medium", bypass_comm: bool = True) -> Dict[str, Any]:
        """
        Runs a query through the dynamic trust-aware collaboration workflow.
        """
        self.logger_layer.clear()
        self.comm_manager.reset()
        self.comm_manager.bypass_enabled = bypass_comm
        
        conversation_id = str(uuid.uuid4())
        task_metadata = {"complexity": complexity, "conversation_id": conversation_id}
        attributions_list = []
        
        self.logger_layer.start_timer("total_execution")
        self.logger_layer.log_event("query_received", {"query": query, "message": f"Received query: '{query}'"})
        
        # Planning phase (Decomposition)
        self.logger_layer.log_event("planning", {"message": "Decomposing user request."})
        subtasks = self.planner.decompose(query)
        self.logger_layer.log_event("planning_complete", {
            "subtasks": subtasks, 
            "message": f"Decomposed query into {len(subtasks)} subtasks."
        })
        
        # Initialize scheduling DAG
        scheduler = DynamicTaskScheduler(subtasks)
        trajectory: List[Dict[str, Any]] = []
        resolved_context: Dict[str, str] = {}
        
        # Retry constraints
        retry_counts: Dict[str, int] = {}
        max_retries = 2
        
        step_index = 0
        task_failed = False
        
        while not scheduler.is_finished() and not task_failed:
            ready_tasks = scheduler.get_ready_tasks()
            
            if not ready_tasks:
                if scheduler.running_tasks:
                    logger.error("Orchestrator Error: Pipeline deadlock detected.")
                    task_failed = True
                    break
                else:
                    break
                    
            for subtask in ready_tasks:
                task_id = subtask["id"]
                role = subtask["assigned_role"]
                scheduler.mark_running(task_id)
                
                agent = self.registry.get_agent(role)
                if not agent:
                    logger.error(f"Execution Error: Missing agent for role '{role}'")
                    scheduler.mark_completed(task_id)
                    continue
                
                # Fetch dynamic trust score (respect static_trust flag)
                trust_score = 1.0 if self.static_trust else self.trust_engine.get_trust(role)
                
                # Compile dependent parent outputs as context
                context_list = []
                for dep_id in subtask.get("dependencies", []):
                    if dep_id in resolved_context:
                        context_list.append({
                            "task_id": dep_id,
                            "response": resolved_context[dep_id]
                        })
                
                # Communication Routing check: Bypassing non-essential agents
                if not self.comm_manager.should_route(
                    current_role="scheduler",
                    next_role=role,
                    calibrated_conf=1.0,
                    trust_score=trust_score,
                    task_metadata=task_metadata
                ):
                    self.comm_manager.log_communication(
                        sender="scheduler",
                        receiver=role,
                        message_snippet="Bypassed by Communication Manager.",
                        confidence=1.0,
                        step_index=step_index
                    )
                    resolved_context[task_id] = f"Bypassed {role} subtask."
                    scheduler.mark_completed(task_id)
                    continue
                
                # Specialized Agent execution
                self.logger_layer.log_event("agent_started", {"agent": agent.name, "role": role})
                agent_output = agent.execute(subtask, context_list)
                self.logger_layer.log_event("agent_completed", {"agent": agent.name, "output": agent_output})
                
                raw_response = agent_output.get("response", "")
                raw_conf = agent_output.get("confidence", 0.5)
                reasoning = agent_output.get("reasoning", "")
                
                # Token accounting
                tokens = agent_output.get("token_usage", {"prompt": 0, "completion": 0})
                self.logger_layer.add_tokens(tokens["prompt"], tokens["completion"])
                
                # Confidence calibration (HTC Platt scaling)
                struct_conf = self.confidence_estimator.estimate_structural_confidence(raw_response, reasoning)
                accum_failures = len(self.long_term_memory.get_all_failures())
                
                # Calibrate confidence if flag is enabled
                if self.use_calibration:
                    calibrated_conf = self.confidence_estimator.calibrate(
                        self_conf=raw_conf,
                        structural_conf=struct_conf,
                        step_index=step_index,
                        accum_failures=accum_failures
                    )
                else:
                    calibrated_conf = raw_conf
                
                # Decision Engine Gating (respect no_decision flag)
                if self.no_decision:
                    decision = "ACCEPT"
                    decision_report = {"decision": "ACCEPT", "reason": "No decision engine active."}
                else:
                    decision_report = self.decision_engine.make_decision(
                        trust_score=trust_score,
                        calibrated_conf=calibrated_conf,
                        task_metadata=task_metadata
                    )
                    decision = decision_report["decision"]
                
                # Verification Manager activation
                if decision == "VERIFY":
                    verifier = self.registry.get_agent("verification")
                    self.logger_layer.log_event("verification_started", {"message": f"Verifying output from {agent.name}."})
                    verify_task = {
                        "id": f"verify_{task_id}",
                        "description": f"Verify: {raw_response}"
                    }
                    verify_output = verifier.execute(verify_task, context_list)
                    
                    is_verified = False
                    if self.use_simulation:
                        # Correct Verification Simulation Logic (Phase 2):
                        # A successful verifier correctly checks generator success.
                        # A failing verifier makes a classification mistake.
                        generator_succeeded = agent_output.get("simulated_success", True)
                        verifier_succeeded = verify_output.get("simulated_success", True)
                        if verifier_succeeded:
                            is_verified = generator_succeeded
                        else:
                            is_verified = not generator_succeeded
                    else:
                        is_verified = "verified" in verify_output.get("response", "").lower()
                        
                    if is_verified:
                        decision = "ACCEPT"
                        decision_report["reason"] += " [Verification Passed]"
                        self.logger_layer.log_event("verification_passed", {"message": "Verification passed."})
                    else:
                        decision = "REJECT"
                        decision_report["reason"] += " [Verification Failed]"
                        self.logger_layer.log_event("verification_failed", {"message": "Verification failed."})
                
                # Record step trajectory
                step_record = {
                    "step": step_index,
                    "task_id": task_id,
                    "task_description": subtask["description"],
                    "role": role,
                    "agent_name": agent.name,
                    "response": raw_response,
                    "raw_confidence": raw_conf,
                    "structural_confidence": struct_conf,
                    "calibrated_conf": calibrated_conf,
                    "trust_score": trust_score,
                    "decision": decision,
                    "simulated": agent_output.get("simulated", False),
                    "simulated_success": agent_output.get("simulated_success", True),
                    "reasoning": reasoning
                }
                trajectory.append(step_record)
                
                # Record to logger calibration dataset
                is_correct = agent_output.get("simulated_success", True) if self.use_simulation else (decision == "ACCEPT")
                self.logger_layer.log_calibration_point(calibrated_conf, is_correct)
                
                # Save to short-term database memory
                self.short_term_memory.save_subtask_state(
                    task_id=task_id,
                    conversation_id=conversation_id,
                    description=subtask["description"],
                    role=role,
                    status=decision,
                    response=raw_response,
                    confidence=raw_conf,
                    calibrated_conf=calibrated_conf,
                    trust=trust_score
                )
                
                self.comm_manager.log_communication(
                    sender=agent.name,
                    receiver="orchestrator",
                    message_snippet=raw_response,
                    confidence=calibrated_conf,
                    step_index=step_index
                )
                
                if decision == "ACCEPT":
                    resolved_context[task_id] = raw_response
                    scheduler.mark_completed(task_id)
                    # Success trust update
                    if not self.static_trust:
                        self.trust_engine.update_trust_on_success(role, w_contrib=1.0)
                        self.long_term_memory.log_trust_transition(role, self.trust_engine.get_trust(role))
                else:
                    # Failure attribution & Penalty triggers
                    retry_count = retry_counts.get(task_id, 0)
                    if retry_count < max_retries:
                        retry_counts[task_id] = retry_count + 1
                        scheduler.running_tasks.remove(task_id)
                        self.logger_layer.log_event("regenerating", {"task_id": task_id, "retry": retry_counts[task_id]})
                        
                        if self.use_fae and not self.static_trust:
                            active_roles = [t["assigned_role"] for t in subtasks if t["id"] in scheduler.completed_tasks or t["id"] == task_id]
                            attr_report = self.failure_attribution.attribute_failure(
                                trajectory=trajectory,
                                error_feedback=decision_report["reason"],
                                is_simulation=self.use_simulation
                            )
                            attributions_list.append(attr_report)
                            failed_role = attr_report["responsible_role"]
                            
                            self.trust_engine.update_trust_on_failure(failed_role, active_roles)
                            self.long_term_memory.log_trust_transition(failed_role, self.trust_engine.get_trust(failed_role))
                            self.long_term_memory.log_failure_attribution(conversation_id, failed_role, step_index, attr_report["reason"])
                        else:
                            # Baseline heuristic failure attribution (blame the current role)
                            attr_report = {
                                "responsible_role": role,
                                "failure_step": step_index,
                                "reason": "Baseline heuristic failure attribution."
                            }
                            attributions_list.append(attr_report)
                            self.long_term_memory.log_failure_attribution(
                                conversation_id, role, step_index, "Dynamic failure attribution bypassed."
                            )
                    else:
                        self.logger_layer.log_event("failure", {"message": f"Subtask {task_id} failed after max retries."})
                        task_failed = True
                        
                step_index += 1

        self.logger_layer.stop_timer("total_execution")
        
        if task_failed:
            final_res = {
                "query": query,
                "response": "Execution terminated. Collaboration reliability parameters were not satisfied.",
                "average_confidence": 0.0,
                "agent_trust_scores": self.trust_engine.get_all_trust_scores(),
                "trajectory_steps": step_index,
                "status": "failed"
            }
        else:
            final_res = self.aggregator.aggregate(query, trajectory, self.trust_engine.get_all_trust_scores())
            final_res["status"] = "success"
            
        self.long_term_memory.save_conversation(conversation_id, query, final_res["response"])
        
        return {
            "conversation_id": conversation_id,
            "result": final_res,
            "trajectory": trajectory,
            "communication_graph": self.comm_manager.get_graph(),
            "metrics": self.logger_layer.get_summary(),
            "attributions": attributions_list
        }
