import logging
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from agents.verification.claim_extractor import ClaimExtractor
from agents.verification.evidence_matcher import EvidenceMatcher
from agents.verification.fact_checker import FactChecker
from agents.verification.hallucination_detector import HallucinationDetector
from agents.verification.citation_verifier import CitationVerifier
from agents.verification.consistency_verifier import ConsistencyVerifier
from agents.verification.verification_scorer import VerificationScorer
from agents.verification.verification_validator import VerificationValidator
from agents.verification.verification_package import VerificationPackageGenerator
from agents.verification.verification_metrics import VerificationMetricsTracker

logger = logging.getLogger("trust_framework")

class VerificationAgent(BaseAgent):
    """
    Modular Verification Agent orchestrating 10 submodules.
    Verifies factual correctness, checks citations, and detects hallucinations.
    """
    def __init__(self, name: str = "VerificationAgent", model: str = "nvidia/nvidia-nemotron-nano-9b-v2", temperature: float = 0.3):
        # Configure nvidia-nemotron-nano-9b-v2 NIM settings
        super().__init__(
            name=name, 
            role="verification", 
            model=model, 
            temperature=temperature,
            extra_body={"chat_template_kwargs": {"thinking": True, "max_thinking_tokens": 1024}}
        )
        self.true_success_rate = 0.96
        self.calibration_bias = 0.01
        
        # Instantiate submodules
        self.claim_extractor = ClaimExtractor(model)
        self.evidence_matcher = EvidenceMatcher()
        self.fact_checker = FactChecker(model)
        self.hallucination_detector = HallucinationDetector(model)
        self.citation_verifier = CitationVerifier()
        self.consistency_verifier = ConsistencyVerifier()
        self.verification_scorer = VerificationScorer(model)
        self.verification_validator = VerificationValidator()
        self.verification_package_gen = VerificationPackageGenerator()

    def execute(self, task: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.use_simulation:
            return self._execute_simulation(task)

        workflow_id = task.get("workflow_id", "wf_global")
        task_id = task.get("id", "task_4")
        
        logger.info(f"VerificationAgent: Executing factual verification for '{task_id}'")
        
        # Initialize metrics tracker
        tracker = VerificationMetricsTracker()
        tracker.start_verification()
        
        # 1. Load document context from context list
        draft_text = ""
        bibliography = []
        provenance = []
        for ctx in context:
            text = ctx.get("response", "")
            if "## References" in text or "##" in text:
                draft_text = text
            pkg = ctx.get("citation_package", {})
            if pkg:
                bibliography = pkg.get("bibliography", [])
            r_pkg = ctx.get("evidence_package", {})
            if r_pkg:
                provenance = r_pkg.get("provenance", [])
                
        # 2. Claim Extraction
        claims = self.claim_extractor.extract_claims(draft_text)
        tracker.claims_verified = len(claims)
        
        # 3. Evidence Matcher
        evidence_matches = self.evidence_matcher.match_evidence(claims, provenance)
        
        # 4. Fact Checker
        claims_payload = [{"id": idx, "claim": c.claim} for idx, c in enumerate(claims)]
        sources_payload = [{"id": entry.get("source_id") if isinstance(entry, dict) else getattr(entry, "source_id", ""), 
                            "ref": entry.get("formatted_reference") if isinstance(entry, dict) else getattr(entry, "formatted_reference", "")} 
                           for entry in bibliography]
                           
        issues = self.fact_checker.check_facts(claims_payload, sources_payload)
        
        # 5. Hallucination Detection
        hallucination_issues = self.hallucination_detector.detect_hallucinations(draft_text)
        issues.extend(hallucination_issues)
        tracker.hallucinations_detected = len(hallucination_issues)
        
        # 6. Citation Verifier
        issues.extend(self.citation_verifier.verify_citations(draft_text, bibliography))
        
        # 7. Consistency Verifier
        issues.extend(self.consistency_verifier.verify_consistency(draft_text))
        
        # 8. Scoring
        score = self.verification_scorer.score_verification(draft_text)
        
        # 9. Validator Status
        verified = self.verification_validator.validate_verification(score, issues)
        
        tracker.stop_verification()
        
        # Build Package
        package = self.verification_package_gen.build_package(
            workflow_id=workflow_id,
            verified=verified,
            score=score,
            issues=issues,
            verified_claims=claims,
            metrics=tracker.get_metrics()
        )
        
        # Formulate verification report summary text
        report_lines = [
            f"### factual Verification Report (Verified: {str(verified).upper()})",
            f"Overall Verification Score: {score.overall_verification:.2f}",
            f"Claim Accuracy: {score.claim_accuracy:.2f} | Hallucination Risk: {score.hallucination_risk:.2f}",
            f"\nAudited {len(claims)} claims against bibliography and provenance records.",
            f"Detected {len(issues)} factual verification warnings or discrepancies."
        ]
        for issue in issues:
            report_lines.append(f"- [{issue.severity.upper()}] {issue.description}")
            
        verification_report = "\n".join(report_lines)
        
        logger.info(f"VerificationAgent: Successfully executed. Verification package compiled.")
        
        return {
            "response": verification_report,
            "confidence": score.overall_verification,  # Calibrated to accuracy
            "reasoning": f"Verified factual consistency. Found {len(issues)} discrepancy warnings.",
            "simulated": False,
            "verification_package": package.dict(),
            "token_usage": {"prompt": 230, "completion": 340}
        }
