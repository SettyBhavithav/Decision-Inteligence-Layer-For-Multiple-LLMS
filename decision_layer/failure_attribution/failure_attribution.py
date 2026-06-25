import json
import logging
import datetime
from typing import Dict, Any, List, Optional
from agents.base_agent import client

from decision_layer.failure_attribution.models import FailurePackage, FailureRecord, RootCause, RecoveryPlan
from decision_layer.failure_attribution.failure_store import FailureStore
from decision_layer.failure_attribution.failure_detector import FailureDetector
from decision_layer.failure_attribution.root_cause_analyzer import RootCauseAnalyzer
from decision_layer.failure_attribution.failure_classifier import FailureClassifier
from decision_layer.failure_attribution.propagation_analyzer import FailurePropagationAnalyzer
from decision_layer.failure_attribution.recovery_planner import RecoveryPlanner
from decision_layer.failure_attribution.attribution_explainer import AttributionExplainer
from decision_layer.failure_attribution.failure_validator import FailureValidator
from decision_layer.failure_attribution.failure_package import FailurePackageGenerator
from decision_layer.failure_attribution.failure_metrics import FailureMetricsTracker

logger = logging.getLogger("trust_framework")

class FailureAttribution:
    """
    Failure Attribution Engine implementing:
    1. Automatic Failure Detection checks.
    2. Softmax-based Root Cause Attribution Confidence.
    3. Actionable Recovery Plan recommendations.
    4. Traced Error Propagation paths.
    
    Includes backward compatible legacy attribute_failure logic.
    """
    def __init__(self, model: str = "nvidia/nvidia-nemotron-nano-9b-v2"):
        self.model = model
        self.store = FailureStore()
        self.detector = FailureDetector()
        self.analyzer = RootCauseAnalyzer()
        self.classifier = FailureClassifier()
        self.propagation_mgr = FailurePropagationAnalyzer()
        self.planner = RecoveryPlanner()
        self.explainer = AttributionExplainer(model)
        self.validator = FailureValidator()
        self.package_gen = FailurePackageGenerator()
        self.tracker = FailureMetricsTracker()

    def run_attribution(self, workflow_id: str, active_agents: List[str], metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main entry point for new pluggable failure attribution.
        Returns serialized FailurePackage dictionary.
        """
        logger.info(f"FailureAttribution: Starting audit for workflow '{workflow_id}'")
        self.tracker.start_timer()
        
        # 1. Failure Detection Check
        detected = self.detector.detect_failure(metrics)
        
        if not detected:
            logger.info(f"FailureAttribution: No failure detected for workflow '{workflow_id}'")
            self.tracker.stop_timer()
            # Return empty/successful failure package
            empty_root = RootCause(responsible_agent="", attribution_confidence=1.0)
            empty_plan = RecoveryPlan(recommended_action="CONTINUE", steps=[])
            package = self.package_gen.build_package(
                workflow_id=workflow_id,
                failure_detected=False,
                failure_type="",
                root_cause=empty_root,
                propagation_graph=[],
                recovery_plan=empty_plan,
                metrics=self.tracker.compile_metrics()
            )
            result = package.model_dump()
            result["responsible_agent"] = ""
            result["attribution_confidence"] = 1.0
            return result
            
        # 2. Classification
        failure_type = self.classifier.classify_failure(metrics)
        
        # 3. Root Cause Attribution (including confidence estimation)
        root_cause = self.analyzer.analyze_root_cause(failure_type, metrics)
        culprit = root_cause.responsible_agent
        
        # 4. Trace Propagation graph
        propagation_graph = self.propagation_mgr.trace_propagation(culprit, active_agents)
        
        # 5. Formulate Recovery Plan
        recovery_plan = self.planner.plan_recovery(failure_type, culprit, metrics)
        
        # 6. Generate explainer report
        explanation = self.explainer.explain_attribution(
            responsible_agent=culprit,
            failure_type=failure_type,
            severity="HIGH",
            metrics=metrics
        )
        
        # 7. Collect telemetry metrics
        self.tracker.log_failure_event(failure_type, culprit, penalty=0.08)
        self.tracker.stop_timer()
        
        # 8. Build and validate package
        comp_metrics = self.tracker.compile_metrics()
        
        package = self.package_gen.build_package(
            workflow_id=workflow_id,
            failure_detected=True,
            failure_type=failure_type,
            root_cause=root_cause,
            propagation_graph=propagation_graph,
            recovery_plan=recovery_plan,
            metrics=comp_metrics
        )
        
        if not self.validator.validate_package(package):
            logger.warning("FailureAttribution: Validation failed for package. Defaulting to REJECT.")
            package.recovery_plan = RecoveryPlan(recommended_action="REJECT", steps=["Discard workflow output."])
            
        self.store.set_failure(workflow_id, package)
        result = package.model_dump()
        # Flatten root_cause for convenient access
        result["responsible_agent"] = package.root_cause.responsible_agent
        result["attribution_confidence"] = package.root_cause.attribution_confidence
        return result

    def attribute_failure(self, 
                          trajectory: List[Dict[str, Any]], 
                          error_feedback: str = "", 
                          is_simulation: bool = False) -> Dict[str, Any]:
        """Legacy helper for backward compatibility."""
        if is_simulation:
            return self._attribute_failure_simulation(trajectory)
        else:
            return self._attribute_failure_llm(trajectory, error_feedback)

    def _attribute_failure_simulation(self, trajectory: List[Dict[str, Any]]) -> Dict[str, Any]:
        for step_idx, step in enumerate(trajectory):
            if step.get("simulated", False) and not step.get("simulated_success", True):
                return {
                    "responsible_role": step.get("role", "unknown").lower(),
                    "failure_step": step_idx,
                    "reason": f"Simulated agent failure (hallucination) occurred during execution."
                }
        
        for step in reversed(trajectory):
            role = step.get("role", "").lower()
            if role not in ["reviewer", "verification", "planner"]:
                return {
                    "responsible_role": role,
                    "failure_step": trajectory.index(step),
                    "reason": "Fallback attribution to primary generator agent."
                }
                
        return {
            "responsible_role": "unknown",
            "failure_step": -1,
            "reason": "Could not identify simulated failure."
        }

    def _attribute_failure_llm(self, trajectory: List[Dict[str, Any]], error_feedback: str) -> Dict[str, Any]:
        formatted_trace = []
        for i, step in enumerate(trajectory):
            formatted_trace.append(
                f"Step {i}: Agent={step.get('agent_name')} (Role={step.get('role')})\n"
                f"Task Description: {step.get('task_description')}\n"
                f"Agent Response: {step.get('response')}\n"
                f"Agent Reasoning: {step.get('reasoning')}\n"
                "----------------------------------------"
            )
            
        trace_str = "\n".join(formatted_trace)
        
        system_prompt = (
            "You are an expert Multi-Agent Failure Attribution Auditor. Your task is to inspect "
            "an execution trace of a collaborative agent workflow and identify which agent and step "
            "was the ROOT CAUSE (decisive error) of the final failure. Ignore downstream errors that "
            "propagated from an upstream mistake—identify the earliest critical error."
        )
        
        user_prompt = (
            f"Execution Trace:\n{trace_str}\n\n"
            f"Final Failure Feedback:\n{error_feedback}\n\n"
            "Analyze the trace step-by-step. Return ONLY a valid JSON object matching this schema:\n"
            "{\n"
            '  "responsible_role": "<role of responsible agent: research/writing/citation/reviewer/verification>",\n'
            '  "failure_step": <integer index of the step where error was introduced>,\n'
            '  "reason": "Clear explanation of why this step caused the failure"\n'
            "}"
        )

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            
            return {
                "responsible_role": parsed.get("responsible_role", "unknown").lower(),
                "failure_step": int(parsed.get("failure_step", -1)),
                "reason": parsed.get("reason", "NVIDIA NIM audit completed analysis.")
            }
        except Exception as e:
            logger.error(f"Failure Attribution NIM audit failed: {e}")
            return {
                "responsible_role": "writing",
                "failure_step": max(0, len(trajectory) - 1),
                "reason": f"Fallback attribution due to audit exception: {str(e)}"
            }
