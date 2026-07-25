"""
INDUS AI — Reasoning Analyzer

Generates a reusable reasoning summary when a case is stored.

Extracts:
  - What worked
  - What failed
  - Why
  - Key lesson

If the caller didn't provide a `reusable_lesson`, the analyzer
auto-generates one from the available data.
"""

import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any

from app.models.decision_intelligence import OutcomeStatusEnum

logger = logging.getLogger(__name__)


@dataclass
class AnalysisSummary:
    """Structured breakdown of a reasoning case."""
    what_worked: str
    what_failed: str
    why: str
    key_lesson: str


class ReasoningAnalyzer:
    """Analyzes resolved decision cases to produce reusable reasoning summaries."""

    @classmethod
    def analyze(
        cls,
        problem_summary: str,
        final_recommendation: str,
        outcome_status: OutcomeStatusEnum,
        confidence_score: float,
        reasoning_steps: Optional[Dict[str, Any]] = None,
        success_score: Optional[float] = None,
        reusable_lesson: Optional[str] = None,
    ) -> AnalysisSummary:
        """
        Generate a structured analysis summary.

        If `reusable_lesson` is provided, it is used as-is for the key_lesson.
        Otherwise, a summary is auto-generated from the available fields.
        """
        what_worked = cls._extract_what_worked(
            outcome_status, final_recommendation, success_score
        )
        what_failed = cls._extract_what_failed(
            outcome_status, final_recommendation
        )
        why = cls._extract_why(reasoning_steps, confidence_score)
        key_lesson = reusable_lesson or cls._generate_lesson(
            problem_summary, final_recommendation, outcome_status, what_worked
        )

        summary = AnalysisSummary(
            what_worked=what_worked,
            what_failed=what_failed,
            why=why,
            key_lesson=key_lesson,
        )

        logger.info(
            "Reasoning analysis complete: outcome=%s, confidence=%.2f",
            outcome_status.value,
            confidence_score,
        )
        return summary

    # ── Private Extraction Methods ────────────────────────────────────────

    @staticmethod
    def _extract_what_worked(
        outcome: OutcomeStatusEnum,
        recommendation: str,
        success_score: Optional[float],
    ) -> str:
        """Determine what worked based on outcome and recommendation."""
        if outcome == OutcomeStatusEnum.SUCCESSFUL:
            score_note = ""
            if success_score is not None:
                score_note = f" (success score: {success_score:.0%})"
            return f"Recommendation was applied successfully{score_note}: {recommendation[:200]}"

        if outcome == OutcomeStatusEnum.PARTIALLY_SUCCESSFUL:
            return f"Recommendation partially worked: {recommendation[:200]}"

        if outcome == OutcomeStatusEnum.FAILED:
            return "No aspects of the recommendation were effective."

        return "Outcome is still pending or unknown."

    @staticmethod
    def _extract_what_failed(
        outcome: OutcomeStatusEnum,
        recommendation: str,
    ) -> str:
        """Determine what failed based on outcome."""
        if outcome == OutcomeStatusEnum.SUCCESSFUL:
            return "Nothing significant failed."

        if outcome == OutcomeStatusEnum.FAILED:
            return f"The recommendation did not resolve the issue: {recommendation[:200]}"

        if outcome == OutcomeStatusEnum.PARTIALLY_SUCCESSFUL:
            return "Some aspects of the recommendation did not fully address the problem."

        return "Outcome not yet determined."

    @staticmethod
    def _extract_why(
        reasoning_steps: Optional[Dict[str, Any]],
        confidence_score: float,
    ) -> str:
        """Extract the reasoning rationale from steps and confidence."""
        parts = []

        if reasoning_steps:
            # Extract key reasoning factors from the JSONB structure
            if isinstance(reasoning_steps, dict):
                for key, value in reasoning_steps.items():
                    if isinstance(value, str) and len(value) > 5:
                        parts.append(f"{key}: {value[:150]}")
                    elif isinstance(value, list):
                        parts.append(f"{key}: {len(value)} factors considered")

        confidence_label = (
            "high" if confidence_score >= 0.8
            else "moderate" if confidence_score >= 0.5
            else "low"
        )
        parts.append(f"Confidence was {confidence_label} ({confidence_score:.0%})")

        return "; ".join(parts) if parts else "Reasoning rationale not captured."

    @staticmethod
    def _generate_lesson(
        problem: str,
        recommendation: str,
        outcome: OutcomeStatusEnum,
        what_worked: str,
    ) -> str:
        """Auto-generate a reusable lesson when none is provided."""
        outcome_label = outcome.value.lower().replace("_", " ")
        problem_short = problem[:100].rstrip(".")

        return (
            f"When encountering '{problem_short}', "
            f"the approach was {outcome_label}. "
            f"{what_worked[:200]}"
        )
