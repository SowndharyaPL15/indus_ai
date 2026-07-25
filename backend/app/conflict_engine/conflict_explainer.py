"""
INDUS AI — Conflict Explainer

Composes detailed, human-readable explanations summarizing detected conflicts
to assist plant engineers in manual analysis and safety reviews.
"""

import logging
from typing import List
from app.conflict_engine.conflict_models import ConflictItem

logger = logging.getLogger(__name__)


class ConflictExplainer:
    """Class to parse conflict lists and generate coherent explanations."""

    @staticmethod
    def explain(conflicts: List[ConflictItem]) -> str:
        """
        Aggregates conflict items and builds a clean markdown explanation paragraph.
        If no conflicts exist, returns a standard reassurance message.
        """
        if not conflicts:
            return "No operational or documentation contradictions detected. Recommendation is clear to proceed."

        explanations = []
        for i, conf in enumerate(conflicts, 1):
            explanations.append(f"Conflict {i} ({conf.type} - {conf.severity} severity):\n• {conf.description}")

        # Summary suggestion
        critical_count = sum(1 for c in conflicts if c.severity == "CRITICAL")
        high_count = sum(1 for c in conflicts if c.severity == "HIGH")

        conclusion = ""
        if critical_count > 0:
            conclusion = "\n\nCRITICAL CONFLICT DETECTED: This recommendation requires mandatory senior engineer or manager review."
        elif high_count > 0:
            conclusion = "\n\nCaution: High severity contradictions found. Verification of the calibration state is recommended."
        else:
            conclusion = "\n\nReview recommended to align SOP guidelines and field practices."

        explanation_text = "\n\n".join(explanations) + conclusion
        logger.info("Conflict explainer generated text: length=%d", len(explanation_text))
        return explanation_text
