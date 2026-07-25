"""
INDUS AI — Confidence Explainer

Maps overall confidence scores to level enums and generates structured,
user-friendly bulleted explanations based on component values and counts.
"""

import logging
from typing import List
from app.idie.evidence_collector import EvidenceBundle
from app.confidence_engine.confidence_models import ComponentScores

logger = logging.getLogger(__name__)


class ConfidenceExplainer:
    """Class to parse confidence scores and generate detailed human-readable explanations."""

    @staticmethod
    def get_level(score: float) -> str:
        """Maps overall score to discrete confidence levels."""
        if score >= 0.90:
            return "VERY_HIGH"
        elif score >= 0.75:
            return "HIGH"
        elif score >= 0.60:
            return "MEDIUM"
        elif score >= 0.40:
            return "LOW"
        else:
            return "VERY_LOW"

    @classmethod
    def explain(
        cls,
        score: float,
        scores: ComponentScores,
        bundle: EvidenceBundle,
    ) -> List[str]:
        """Generates bullet points explaining the overall confidence score based on input details."""
        level = cls.get_level(score)
        explanations = []

        # ── Explain Documents ─────────────────────────────────────────────
        doc_count = len(bundle.documents)
        if doc_count > 0:
            explanations.append(f"{doc_count} supporting document(s) and operational manuals retrieved")
            if scores.documents >= 0.80:
                explanations.append("High quality vector similarity matches found in retrieved manual chunks")
        else:
            explanations.append("No official documentation chunks retrieved from knowledge base")

        # ── Explain Factory Memory ────────────────────────────────────────
        mem_count = len(bundle.factory_memories)
        if mem_count > 0:
            explanations.append(f"{mem_count} living factory memory solution(s) contributed by plant engineers")
            validated_count = sum(1 for m in bundle.factory_memories if m.validated)
            if validated_count > 0:
                explanations.append(f"{validated_count} engineer memory record(s) fully validated by quality protocols")
            high_rated = sum(1 for m in bundle.factory_memories if m.rating >= 4)
            if high_rated > 0:
                explanations.append(f"{high_rated} memory entry/entries rated highly useful (4+ stars) by plant staff")
        else:
            explanations.append("No living factory memory solutions found for this category of issue")

        # ── Explain Similar Cases (Reasoning) ─────────────────────────────
        cbr_count = len(bundle.reasoning_cases)
        if cbr_count > 0:
            explanations.append(f"{cbr_count} similar historical case(s) retrieved from Reasoning CBR memory")
            successful_count = sum(1 for c in bundle.reasoning_cases if c.outcome_status == "SUCCESSFUL")
            if successful_count > 0:
                explanations.append(f"{successful_count} historical resolution(s) proven highly successful")
            high_match = sum(1 for c in bundle.reasoning_cases if c.similarity_score >= 0.80)
            if high_match > 0:
                explanations.append(f"Spindle/incident similarity score is strong ({max(c.similarity_score for c in bundle.reasoning_cases):.0%})")
        else:
            explanations.append("No historically resolved cases matched this incident profile")

        # ── Explain Knowledge Graph ───────────────────────────────────────
        graph_count = len(bundle.graph_context)
        if graph_count > 0:
            explanations.append(f"Knowledge graph maps {graph_count} connected factory entities to this incident context")
            if scores.graph >= 0.75:
                explanations.append("Strong relationships established across machines, incidents, sops, and compliance rules")
        else:
            explanations.append("Knowledge Graph context shows this incident type is poorly linked to other entities")

        # ── Explain Intent ────────────────────────────────────────────────
        if scores.intent >= 0.85:
            explanations.append("Cognitive Intent detection aligns strongly with historical incident profiles")

        # Formulate explanations summary header
        final_list = [f"Confidence is {level} ({score:.0%}) because:"]
        for exp in explanations[:6]:  # Cap at top 6 details for summary cleanliness
            final_list.append(f"• {exp}")

        logger.info("Confidence explained: level=%s, bullets=%d", level, len(final_list) - 1)
        return final_list
