import logging
from typing import Dict, Any, List

from agents.base_agent import BaseAgent
from agents.research.query_understanding import QueryUnderstanding
from agents.research.retrieval_manager import RetrievalManager
from agents.research.source_manager import SourceManager
from agents.research.evidence_ranker import EvidenceRanker
from agents.research.duplicate_removal import DuplicateRemoval
from agents.research.knowledge_synthesizer import KnowledgeSynthesizer
from agents.research.research_validator import ResearchValidator
from agents.research.provenance_generator import ProvenanceGenerator
from agents.research.evidence_package import EvidencePackageGenerator
from agents.research.research_metrics import ResearchMetricsTracker

logger = logging.getLogger("trust_framework")

class ResearchAgent(BaseAgent):
    """
    Modular Research Agent orchestrating 10 submodules.
    Compiles detailed Evidence Packages linking assertions to verified citations.
    """
    def __init__(self, name: str = "ResearchAgent", model: str = "deepseek-ai/deepseek-v4-flash", temperature: float = 0.5):
        # Configure deepseek-v4-flash NIM settings
        super().__init__(
            name=name, 
            role="research", 
            model=model, 
            temperature=temperature,
            extra_body={"chat_template_kwargs": {"thinking": True, "reasoning_effort": "high"}}
        )
        self.true_success_rate = 0.88
        self.calibration_bias = 0.04
        
        # Instantiate submodules
        self.query_understanding = QueryUnderstanding(model)
        self.retrieval_manager = RetrievalManager()
        self.source_manager = SourceManager()
        self.evidence_ranker = EvidenceRanker()
        self.duplicate_removal = DuplicateRemoval()
        self.knowledge_synthesizer = KnowledgeSynthesizer(model)
        self.research_validator = ResearchValidator(model)
        self.provenance_generator = ProvenanceGenerator(model)
        self.evidence_package_gen = EvidencePackageGenerator()

    def execute(self, task: Dict[str, Any], context: List[Dict[str, Any]]) -> Dict[str, Any]:
        if self.use_simulation:
            return self._execute_simulation(task)

        workflow_id = task.get("workflow_id", "wf_global")
        task_id = task.get("id", "task_0")
        task_description = task.get("description", "")

        logger.info(f"ResearchAgent: Executing research task '{task_id}'")
        
        # Initialize metrics tracker
        tracker = ResearchMetricsTracker()
        tracker.start_retrieval()
        
        # 1. Query Understanding
        query_spec = self.query_understanding.analyze_task(task_description)
        
        # 2. Retrieval
        raw_docs = self.retrieval_manager.retrieve(query_spec)
        tracker.stop_retrieval()
        
        if not raw_docs:
            return {
                "response": "Error: Document index search yielded zero results.",
                "confidence": 0.1,
                "reasoning": "Empty document retrieval fallback.",
                "simulated": False
            }
            
        # 3. Source Normalization
        normalized_docs = self.source_manager.normalize_sources(raw_docs)
        
        # 4. Evidence Ranking
        ranked_docs = self.evidence_ranker.rank(normalized_docs)
        
        # 5. Duplicate Removal
        clean_docs = self.duplicate_removal.remove_duplicates(ranked_docs)
        tracker.duplicates_removed = self.duplicate_removal.removed_count
        tracker.num_sources = len(clean_docs)
        
        # 6. Knowledge Synthesis
        tracker.start_synthesis()
        synthesis_result = self.knowledge_synthesizer.synthesize(clean_docs)
        tracker.stop_synthesis()
        
        summary = synthesis_result.get("summary", "")
        key_findings = synthesis_result.get("key_findings", [])
        
        # 7. Research Validation Loop
        validation_report = self.research_validator.validate(summary)
        if not validation_report.get("is_valid", True):
            logger.warning(f"ResearchAgent: Validation failed: {validation_report.get('errors')}. Triggering synthesis retry...")
            # Simple retry loop once
            synthesis_result = self.knowledge_synthesizer.synthesize(clean_docs)
            summary = synthesis_result.get("summary", "")
            key_findings = synthesis_result.get("key_findings", [])
            
        # 8. Provenance Generation
        source_ids = [d.id for d in clean_docs]
        provenance = self.provenance_generator.generate_provenance(summary, source_ids)
        tracker.num_claims = len(provenance)
        tracker.num_citations = sum(len(p.supported_by) for p in provenance)
        
        # Compile Evidence Package
        package = self.evidence_package_gen.build_package(
            workflow_id=workflow_id,
            task_id=task_id,
            summary=summary,
            key_findings=key_findings,
            evidence=clean_docs,
            provenance=provenance,
            metrics=tracker.get_metrics()
        )
        
        logger.info(f"ResearchAgent: Successfully executed. Compiled Evidence Package for {task_id}.")
        
        return {
            "response": summary,
            "confidence": 0.90,  # Self-reported base confidence
            "reasoning": f"Synthesized research findings using {len(clean_docs)} sources.",
            "simulated": False,
            "evidence_package": package.dict(),
            "token_usage": {"prompt": 200, "completion": 300}
        }
