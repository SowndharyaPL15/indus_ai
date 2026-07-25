"""
INDUS AI — IDIE v2 Evidence Ranker

Assigns scores and weights to the collected evidence sources to calculate a
unified/fused confidence score.

Default weights:
  - RAG Documents: 0.35
  - Factory Memory: 0.25
  - Reasoning Memory: 0.25
  - Knowledge Graph: 0.15
"""

import logging
from typing import Dict, Optional
from app.idie.evidence_collector import EvidenceBundle

logger = logging.getLogger(__name__)


class EvidenceRanker:
    """Ranks and weights different evidence sources to compute a unified confidence score."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        # Default configurable weights
        self.weights = weights or {
            "rag": 0.35,
            "factory_memory": 0.25,
            "reasoning": 0.25,
            "knowledge_graph": 0.15,
        }
        # Normalize weights to sum to 1.0
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def compute_fused_confidence(self, bundle: EvidenceBundle) -> float:
        """
        Calculates a unified confidence score based on the weighted components:
        - RAG: uses QueryResponse confidence (or 0.0 if RAG response is empty/None)
        - Factory Memory: heuristic based on ratings of validated records (default 0.7 if found, scaled by average rating/5.0)
        - Reasoning Memory: uses maximum similarity score found (or 0.0 if none)
        - Knowledge Graph: heuristic based on node/edge density (capped at 1.0)
        """
        confidences = {
            "rag": 0.0,
            "factory_memory": 0.0,
            "reasoning": 0.0,
            "knowledge_graph": 0.0,
        }

        # 1. RAG Confidence
        if bundle.raw_rag_response:
            confidences["rag"] = max(0.0, min(bundle.raw_rag_response.confidence, 1.0))

        # 2. Factory Memory Confidence Heuristic
        if bundle.factory_memories:
            avg_rating = sum(r.rating for r in bundle.factory_memories) / len(bundle.factory_memories)
            # Map rating (usually 1-5) to 0.0 - 1.0
            rating_score = min(max(avg_rating / 5.0, 0.5), 1.0)
            confidences["factory_memory"] = rating_score

        # 3. Similar Cases Similarity score
        if bundle.reasoning_cases:
            # Use the best match's similarity score
            max_sim = max(c.similarity_score for c in bundle.reasoning_cases)
            confidences["reasoning"] = max_sim

        # 4. Knowledge Graph density heuristic
        if bundle.graph_context:
            # More connections to this case indicates higher contextual certainty
            confidences["knowledge_graph"] = min(len(bundle.graph_context) / 5.0, 1.0)

        # Compute weighted sum
        fused = 0.0
        for source, weight in self.weights.items():
            fused += confidences[source] * weight

        logger.info(
            "Confidence fusion: RAG=%.2f, Mem=%.2f, CBR=%.2f, Graph=%.2f -> Fused=%.3f",
            confidences["rag"], confidences["factory_memory"],
            confidences["reasoning"], confidences["knowledge_graph"], fused
        )

        return round(fused, 2)
