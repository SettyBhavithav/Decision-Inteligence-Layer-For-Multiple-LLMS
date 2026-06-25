import logging
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from agents.reviewer.document_loader import DocumentLoader
from agents.reviewer.structure_reviewer import StructureReviewer
from agents.reviewer.logic_reviewer import LogicReviewer
from agents.reviewer.claim_reviewer import ClaimReviewer
from agents.reviewer.citation_reviewer import CitationReviewer
from agents.reviewer.consistency_reviewer import ConsistencyReviewer
from agents.reviewer.quality_scorer import QualityScorer
from agents.reviewer.suggestion_generator import SuggestionGenerator
from agents.reviewer.review_validator import ReviewValidator
from agents.reviewer.review_package import ReviewPackageGenerator
from agents.reviewer.review_metrics import ReviewMetricsTracker

logger = logging.getLogger("trust_framework")

class ReviewerAgent(BaseAgent):
    """
    Modular Reviewer Agent orchestrating 11 submodules.
    Audits document layouts, logical statements, and drafts quality reports.
    """
    def __init__(self, name: str = "ReviewerAgent", model: str = "nvidia/nvidia-nemotron-nano-9b-v2", temperature: float = 0.5):
        # Configure nvidia-nemotron-nano-9b-v2 NIM settings
        super().__init__(
            name=name, 
            role="reviewer", 
            model=model, 
            temperature=temperature,
            extra_body={"chat_template_kwargs": {"thinking": True, "max_thinking_tokens": 1024}}
        )
        self.true_success_rate = 0.90
        self.calibration_bias = 0.05
        
        # Instantiate submodules
        self.document_loader = DocumentLoader()
        self.structure_reviewer = StructureReviewer()
        self.logic_reviewer = LogicReviewer(model)
        self.claim_reviewer = ClaimReviewer(model)
        self.citation_reviewer = CitationReviewer(model)
        self.consistency_reviewer = ConsistencyReviewer()
        self.quality_scorer = QualityScorer(model)
        self.suggestion_generator = SuggestionGenerator()
        self.review_validator = ReviewValidator()
        self.review_package_gen = ReviewPackageGenerator()

    def execute(self, task: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.use_simulation:
            return self._execute_simulation(task)

        workflow_id = task.get("workflow_id", "wf_global")
        task_id = task.get("id", "task_3")
        
        logger.info(f"ReviewerAgent: Executing QA review for '{task_id}'")
        
        # Initialize metrics tracker
        tracker = ReviewMetricsTracker()
        tracker.start_review()
        
        # 1. Load document context from context list
        draft_text = ""
        citation_package = {}
        for ctx in context:
            text = ctx.get("response", "")
            if "## References" in text or "##" in text:
                draft_text = text
            pkg = ctx.get("citation_package", {})
            if pkg:
                citation_package = pkg
                
        doc_data = self.document_loader.load_document(
            draft_package={"draft": draft_text, "sections": [], "workflow_id": workflow_id},
            citation_package=citation_package
        )
        
        # 2. Review structure
        issues = self.structure_reviewer.review_structure(doc_data["draft"])
        
        # 3. Review logic
        issues.extend(self.logic_reviewer.review_logic(doc_data["draft"]))
        
        # 4. Review claims
        issues.extend(self.claim_reviewer.review_claims(doc_data["draft"]))
        
        # 5. Review citations
        issues.extend(self.citation_reviewer.review_citations(doc_data["draft"]))
        
        # 6. Review consistency
        issues.extend(self.consistency_reviewer.review_consistency(doc_data["draft"]))
        
        # 7. Quality Scorer
        score = self.quality_scorer.score_quality(doc_data["draft"])
        
        # 8. Suggestion Generator
        suggestions = self.suggestion_generator.generate_suggestions(issues)
        
        tracker.issues_count = len(issues)
        tracker.suggestions_count = len(suggestions)
        
        # 9. Review Validator Status
        status = self.review_validator.validate_review(score, issues)
        
        tracker.stop_review()
        
        # Build Review Package
        package = self.review_package_gen.build_package(
            workflow_id=workflow_id,
            status=status,
            score=score,
            issues=issues,
            suggestions=suggestions,
            metrics=tracker.get_metrics()
        )
        
        # Formulate review report summary text
        report_lines = [
            f"### QA Review Report (Status: {status.upper()})",
            f"Overall Quality Score: {score.overall_quality:.2f}",
            f"Structure Score: {score.structure_score:.2f} | Logic: {score.logic_score:.2f} | Citations: {score.citation_score:.2f}",
            f"\nDetected {len(issues)} issues and generated {len(suggestions)} suggestions.",
            "\n#### Suggested Improvements:"
        ]
        for sug in suggestions:
            report_lines.append(f"- {sug.suggestion}")
            
        review_report = "\n".join(report_lines)
        
        logger.info(f"ReviewerAgent: Successfully executed. Review report compiled.")
        
        return {
            "response": review_report,
            "confidence": score.overall_quality,  # Calibrated to quality score
            "reasoning": f"Reviewed document structure and quality. Found {len(issues)} issues.",
            "simulated": False,
            "review_package": package.dict(),
            "token_usage": {"prompt": 210, "completion": 320}
        }
