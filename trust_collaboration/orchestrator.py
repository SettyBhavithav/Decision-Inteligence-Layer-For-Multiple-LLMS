import uuid
import logging
from typing import Dict, Any, List

# Import all modular layers
from trust_collaboration.planning.planner import PlannerAgent
from trust_collaboration.planning.scheduler import DynamicTaskScheduler
from trust_collaboration.agents.registry import AgentRegistry
from trust_collaboration.agents.specialized import (
    ResearchAgent, WritingAgent, CitationAgent, ReviewerAgent, VerificationAgent
)
from trust_collaboration.research.trust import TrustEngine
from trust_collaboration.research.confidence import ConfidenceEstimator
from trust_collaboration.research.decision import DecisionEngine
from trust_collaboration.research.communication import CommunicationManager
from trust_collaboration.research.failure import FailureAttribution
from trust_collaboration.memory.store import MemoryStore
from trust_collaboration.memory.aggregator import ResponseAggregator
from trust_collaboration.logging_layer import EventLogger

logger = logging.getLogger("trust_framework")

class FrameworkOrchestrator:
    """
    Framework Orchestrator (Central controller).
    Implements the complete 15-step sequence flow defined in SISD Phase 2B.
    """
    def __init__(self, use_simulation: bool = False, db_path: str = "metadata.db"):
        self.use_simulation = use_simulation
        
        # Initialize modules
        self.planner = PlannerAgent()
        self.planner.use_simulation = use_simulation
        
        self.trust_engine = TrustEngine()
        self.confidence_estimator = ConfidenceEstimator()
        self.decision_engine = DecisionEngine()
        self.comm_manager = CommunicationManager()
        self.failure_attribution = FailureAttribution()
        self.memory = MemoryStore(db_path)
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
        
        # Apply simulation mode to registry
        if self.use_simulation:
            for role in self.registry.list_roles():
                agent = self.registry.get_agent(role)
                if agent:
                    agent.use_simulation = True

    def run_task(self, query: str, complexity: str = "medium") -> Dict[str, Any]:
        """
        Executes a task end-to-end, applying trust and confidence calibration.
        """
        self.logger_layer.clear()
        self.comm_manager.reset()
        
        conversation_id = str(uuid.uuid4())
        task_metadata = {"complexity": complexity, "conversation_id": conversation_id}
        
        self.logger_layer.start_timer("total_execution")
        self.logger_layer.log_event("query_received", {"query": query, "message": f"Received query: '{query}'"})
        
        # Step 4: Decomposition via Planner Agent
        self.logger_layer.log_event("planning", {"message": "Decomposing query into subtasks."})
        subtasks = self.planner.decompose(query)
        self.logger_layer.log_event("planning_complete", {
            "subtasks": subtasks, 
            "message": f"Planner created {len(subtasks)} subtasks."
        })
        
        # Step 5: Initialize Scheduler
        scheduler = DynamicTaskScheduler(subtasks)
        
        # Trajectory list to store execution traces
        trajectory: List[Dict[str, Any]] = []
        # Store resolved context outputs: {subtask_id: response}
        resolved_context: Dict[str, str] = {}
        
        # Tracking retries to avoid infinite loops
        retry_counts: Dict[str, int] = {}
        max_retries = 2
        
        # Dynamic execution loop
        step_index = 0
        task_failed = False
        
        while not scheduler.is_finished() and not task_failed:
            ready_tasks = scheduler.get_ready_tasks()
            
            if not ready_tasks:
                if scheduler.running_tasks:
                    # In a multi-threaded system we would wait, here we break if deadlock
                    logger.error("Deadlock: No ready tasks, but scheduler not finished.")
                    task_failed = True
                    break
                else:
                    break
                    
            for subtask in ready_tasks:
                task_id = subtask["id"]
                role = subtask["assigned_role"]
                scheduler.mark_running(task_id)
                
                # Fetch agent from registry
                agent = self.registry.get_agent(role)
                if not agent:
                    logger.error(f"Agent role '{role}' not registered in registry.")
                    scheduler.mark_completed(task_id)
                    continue
                
                # Get current trust score for agent role
                trust_score = self.trust_engine.get_trust(role)
                
                # Compile context from dependencies
                context_list = []
                for dep_id in subtask.get("dependencies", []):
                    if dep_id in resolved_context:
                        context_list.append({
                            "task_id": dep_id,
                            "response": resolved_context[dep_id]
                        })
                
                # Adaptive Communication Manager check:
                # Decide if we should route to this agent or bypass it
                if not self.comm_manager.should_route(
                    current_role="scheduler",
                    next_role=role,
                    calibrated_conf=1.0,  # default prior
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
                    # Create dummy response
                    resolved_context[task_id] = f"Bypassed {role} subtask."
                    scheduler.mark_completed(task_id)
                    continue
                
                # Step 6: Specialized Agent Execution
                self.logger_layer.log_event("agent_started", {"agent": agent.name, "role": role})
                agent_output = agent.execute(subtask, context_list)
                self.logger_layer.log_event("agent_completed", {"agent": agent.name, "output": agent_output})
                
                raw_response = agent_output.get("response", "")
                raw_conf = agent_output.get("confidence", 0.5)
                reasoning = agent_output.get("reasoning", "")
                
                # Step 8: Confidence Estimation & Calibration
                struct_conf = self.confidence_estimator.estimate_structural_confidence(raw_response, reasoning)
                accum_failures = len(self.memory.get_all_failures())
                
                calibrated_conf = self.confidence_estimator.calibrate(
                    self_conf=raw_conf,
                    structural_conf=struct_conf,
                    step_index=step_index,
                    accum_failures=accum_failures
                )
                
                # Step 9: Decision Engine Gating
                decision_report = self.decision_engine.make_decision(
                    trust_score=trust_score,
                    calibrated_conf=calibrated_conf,
                    task_metadata=task_metadata
                )
                
                decision = decision_report["decision"]
                
                # Step 11: Verification Module
                if decision == "VERIFY":
                    verifier = self.registry.get_agent("verification")
                    self.logger_layer.log_event("verification_started", {"message": f"Verifying output from {agent.name}."})
                    verify_task = {
                        "id": f"verify_{task_id}",
                        "description": f"Verify: {raw_response}"
                    }
                    verify_output = verifier.execute(verify_task, context_list)
                    
                    # Determine if verification succeeded
                    # In simulation, it matches verification success. In real, checks keyword
                    is_verified = False
                    if self.use_simulation:
                        is_verified = verify_output.get("simulated_success", True)
                    else:
                        is_verified = "verified" in verify_output.get("response", "").lower()
                        
                    if is_verified:
                        decision = "ACCEPT"
                        decision_report["reason"] += " [Verification Passed]"
                        self.logger_layer.log_event("verification_passed", {"message": "Verification passed, promoting response to ACCEPT."})
                    else:
                        decision = "REJECT"
                        decision_report["reason"] += " [Verification Failed]"
                        self.logger_layer.log_event("verification_failed", {"message": "Verification failed, demoting response to REJECT."})
                
                # Record this step in the trajectory
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
                
                # Step 13: Log subtask execution in Memory
                self.memory.save_subtask(
                    task_id=task_id,
                    conv_id=conversation_id,
                    desc=subtask["description"],
                    role=role,
                    status=decision,
                    resp=raw_response,
                    conf=raw_conf,
                    calibrated_conf=calibrated_conf,
                    trust=trust_score
                )
                
                # Log communication link
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
                    # Step 13: Success Trust update
                    self.trust_engine.update_trust_on_success(role, w_contrib=1.0)
                    self.memory.log_trust(role, self.trust_engine.get_trust(role))
                else:
                    # Reject / Regenerate logic
                    retry_count = retry_counts.get(task_id, 0)
                    if retry_count < max_retries:
                        retry_counts[task_id] = retry_count + 1
                        scheduler.running_tasks.remove(task_id) # Release lock so it runs again
                        self.logger_layer.log_event("regenerating", {"task_id": task_id, "retry": retry_counts[task_id]})
                        
                        # Step 12: Failure Attribution & Penalty (even on retry)
                        active_roles = [t["assigned_role"] for t in subtasks if t["id"] in scheduler.completed_tasks or t["id"] == task_id]
                        attr_report = self.failure_attribution.attribute_failure(
                            trajectory=trajectory,
                            error_feedback=decision_report["reason"],
                            is_simulation=self.use_simulation
                        )
                        failed_role = attr_report["responsible_role"]
                        
                        self.trust_engine.update_trust_on_failure(failed_role, active_roles)
                        self.memory.log_trust(failed_role, self.trust_engine.get_trust(failed_role))
                        self.memory.log_failure(conversation_id, failed_role, step_index, attr_report["reason"])
                    else:
                        self.logger_layer.log_event("failure", {"message": f"Subtask {task_id} failed after {max_retries} retries."})
                        task_failed = True
                        
                step_index += 1

        self.logger_layer.stop_timer("total_execution")
        
        # Step 15: Compile final response or report overall failure
        if task_failed:
            final_res = {
                "query": query,
                "response": "Failed to complete the query because collaboration reliability checks were not satisfied.",
                "average_confidence": 0.0,
                "agent_trust_scores": self.trust_engine.get_all_trust_scores(),
                "trajectory_steps": step_index,
                "status": "failed"
            }
        else:
            final_res = self.aggregator.aggregate(query, trajectory, self.trust_engine.get_all_trust_scores())
            final_res["status"] = "success"
            
        self.memory.save_conversation(conversation_id, query, final_res["response"])
        
        return {
            "conversation_id": conversation_id,
            "result": final_res,
            "trajectory": trajectory,
            "communication_graph": self.comm_manager.get_graph(),
            "metrics": self.logger_layer.get_summary()
        }
