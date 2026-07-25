"""
INDUS AI — Confidence Calculator

Calculates component-level and overall confidence scores programmatically based on
structured heuristics across the 5 evidence sources. All scores are normalized [0.0 - 1.0].
"""

import logging
from typing import Dict, Tuple, Optional
from app.idie.evidence_collector import EvidenceBundle
from app.confidence_engine.confidence_models import ComponentScores

logger = logging.getLogger(__name__)


class ConfidenceCalculator:
    """Computes evidence scores and fuses them using configurable weights."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        # Configurable weights matching user specification
        self.weights = weights or {
            "documents": 0.35,
            "factory_memory": 0.20,
            "reasoning": 0.20,
            "graph": 0.15,
            "intent": 0.10,
        }
        # Normalize weights to ensure total is exactly 1.0
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def calculate_overall(
        self,
        bundle: EvidenceBundle,
        intent_confidence: float,
    ) -> Tuple[float, ComponentScores]:
        """Calculates all component scores and computes the final weighted score."""
        doc_score = self.calculate_documents_score(bundle)
        mem_score = self.calculate_factory_memory_score(bundle)
        reason_score = self.calculate_reasoning_score(bundle)
        graph_score = self.calculate_graph_score(bundle)
        intent_score = self.calculate_intent_score(intent_confidence)

        scores = ComponentScores(
            documents=round(doc_score, 4),
            factory_memory=round(mem_score, 4),
            reasoning=round(reason_score, 4),
            graph=round(graph_score, 4),
            intent=round(intent_score, 4)
        )

        overall = (
            scores.documents * self.weights["documents"] +
            scores.factory_memory * self.weights["factory_memory"] +
            scores.reasoning * self.weights["reasoning"] +
            scores.graph * self.weights["graph"] +
            scores.intent * self.weights["intent"]
        )

        return round(overall, 4), scores

    # ── Component Heuristics ──────────────────────────────────────────────

    @staticmethod
    def calculate_documents_score(bundle: EvidenceBundle) -> float:
        """
        Document evidence heuristic [0.0 - 1.0]:
        - Max chunk similarity score (40%)
        - Chunk count coverage (30%) - max at 5 chunks
        - Citation quality average score (30%)
        """
        if not bundle.citations:
            return 0.0

        scores = [c.score for c in bundle.citations]
        max_sim = max(scores)
        avg_cit = sum(scores) / len(scores)
        chunk_coverage = min(len(bundle.citations) / 5.0, 1.0)

        # Map to 0-1 range (max_sim is usually between 0 and 1)
        score = 0.4 * max_sim + 0.3 * chunk_coverage + 0.3 * avg_cit
        return min(max(score, 0.0), 1.0)

    @staticmethod
    def calculate_factory_memory_score(bundle: EvidenceBundle) -> float:
        """
        Living memory heuristic [0.0 - 1.0]:
        - Rating average (50%) - scaled by 1-5 rating range
        - Validation status percentage (30%)
        - Reuse frequency count (20%) - capped at 10 times reused
        """
        if not bundle.factory_memories:
            return 0.0

        ratings = [m.rating for m in bundle.factory_memories]
        avg_rating = sum(ratings) / len(ratings)
        rating_score = min(avg_rating / 5.0, 1.0)

        validation_score = sum(1.0 if m.validated else 0.5 for m in bundle.factory_memories) / len(bundle.factory_memories)
        
        reuses = [m.times_reused for m in bundle.factory_memories]
        avg_reuse = sum(reuses) / len(reuses)
        reuse_score = min(avg_reuse / 10.0, 1.0)

        score = 0.5 * rating_score + 0.3 * validation_score + 0.2 * reuse_score
        return min(max(score, 0.0), 1.0)

    @staticmethod
    def calculate_reasoning_score(bundle: EvidenceBundle) -> float:
        """
        Reasoning memory (CBR) heuristic [0.0 - 1.0]:
        - Similarity score max (40%)
        - Past success score average (40%)
        - Case outcome status factor (20%)
        """
        if not bundle.reasoning_cases:
            return 0.0

        similarities = [c.similarity_score for c in bundle.reasoning_cases]
        max_sim = max(similarities)

        successes = []
        outcomes = []
        for c in bundle.reasoning_cases:
            # Success score extraction
            successes.append(c.success_score if c.success_score is not None else (1.0 if c.outcome_status == "SUCCESSFUL" else 0.5))
            
            # Outcome mapping
            status = c.outcome_status
            if status == "SUCCESSFUL":
                outcomes.append(1.0)
            elif status == "PARTIALLY_SUCCESSFUL":
                outcomes.append(0.7)
            elif status == "FAILED":
                outcomes.append(0.2)
            else:
                outcomes.append(0.5)

        avg_success = sum(successes) / len(successes)
        avg_outcome = sum(outcomes) / len(outcomes)

        score = 0.4 * max_sim + 0.4 * avg_success + 0.2 * avg_outcome
        return min(max(score, 0.0), 1.0)

    @staticmethod
    def calculate_graph_score(bundle: EvidenceBundle) -> float:
        """
        Knowledge Graph heuristic [0.0 - 1.0]:
        - Connected entity count (40%) - capped at 10 entities
        - Depth closeness weight (30%) - 1-hop = 1.0, 2-hop = 0.7
        - Context completeness (30%) - fraction of node types represented (out of 9 NodeTypes)
        """
        if not bundle.graph_context:
            return 0.0

        count_score = min(len(bundle.graph_context) / 10.0, 1.0)

        depths = [1.0 if g.depth == 1 else 0.7 for g in bundle.graph_context]
        avg_depth = sum(depths) / len(depths)

        unique_types = {g.entity_type for g in bundle.graph_context}
        completeness = len(unique_types) / 9.0  # 9 unique NodeType enums

        score = 0.4 * count_score + 0.3 * avg_depth + 0.3 * completeness
        return min(max(score, 0.0), 1.0)

    @staticmethod
    def calculate_intent_score(intent_confidence: float) -> float:
        """Intent mapping [0.0 - 1.0]."""
        return min(max(intent_confidence, 0.0), 1.0)
