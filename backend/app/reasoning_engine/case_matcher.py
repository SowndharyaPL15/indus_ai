"""
INDUS AI — Case Matcher

Finds similar previously-solved Decision Cases using Case-Based Reasoning (CBR).

Similarity strategy is modular:
  - Current: Keyword (ILIKE) retrieval + Jaccard word-overlap scoring
  - Future:  Swap in EmbeddingSimilarityStrategy via the SimilarityStrategy protocol

Input:  problem text (query string)
Output: Top-N similar solved cases with similarity scores
"""

import logging
import re
from typing import List, Protocol, runtime_checkable
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision_intelligence import ReasoningMemory, OutcomeStatusEnum
from app.reasoning_engine.reasoning_repository import ReasoningRepository

logger = logging.getLogger(__name__)

# Stop words to exclude from Jaccard comparison
_STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "need", "must",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "as",
    "into", "through", "during", "before", "after", "above", "below",
    "and", "but", "or", "nor", "not", "so", "yet", "both", "either",
    "it", "its", "this", "that", "these", "those", "what", "which", "who",
    "i", "me", "my", "we", "our", "you", "your", "he", "she", "they",
})


# ── Similarity Strategy Protocol ─────────────────────────────────────────────

@runtime_checkable
class SimilarityStrategy(Protocol):
    """
    Protocol for similarity scoring strategies.
    Implement this to swap in embedding-based or ML-based similarity.
    """

    def score(self, query: str, record: ReasoningMemory) -> float:
        """Return a similarity score between 0.0 and 1.0."""
        ...


# ── Scored Result ─────────────────────────────────────────────────────────────

@dataclass
class ScoredCase:
    """A ReasoningMemory record with a computed similarity score."""
    record: ReasoningMemory
    similarity_score: float


# ── Default Strategy: Jaccard + Bonus Signals ─────────────────────────────────

class KeywordSimilarityStrategy:
    """
    Word-overlap similarity using Jaccard index with bonus signals.

    Scoring:
      base    = Jaccard(query_tokens, problem_summary_tokens)
      bonus   = +0.10 if SUCCESSFUL outcome
                +0.05 * confidence_score
                +0.05 * success_score (if available)
      final   = min(base + bonus, 1.0)
    """

    @staticmethod
    def _tokenize(text: str) -> set[str]:
        """Extract lowercase word tokens, excluding stop words."""
        words = set(re.findall(r"[a-z0-9]+", text.lower()))
        return words - _STOP_WORDS

    def score(self, query: str, record: ReasoningMemory) -> float:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return 0.0

        # Combine problem summary + recommendation + lesson for matching
        record_text = " ".join(filter(None, [
            record.problem_summary,
            record.final_recommendation,
            record.reusable_lesson or "",
        ]))
        record_tokens = self._tokenize(record_text)

        if not record_tokens:
            return 0.0

        # Jaccard similarity
        intersection = query_tokens & record_tokens
        union = query_tokens | record_tokens
        base_score = len(intersection) / len(union) if union else 0.0

        # Bonus signals
        bonus = 0.0
        if record.outcome_status == OutcomeStatusEnum.SUCCESSFUL:
            bonus += 0.10
        bonus += 0.05 * record.confidence_score
        if record.success_score is not None:
            bonus += 0.05 * record.success_score

        return min(base_score + bonus, 1.0)


# ── Case Matcher ──────────────────────────────────────────────────────────────

class CaseMatcher:
    """
    Finds similar previously-solved Decision Cases.

    Uses a two-phase approach:
      1. Candidate retrieval  — ILIKE keyword search via ReasoningRepository
      2. Similarity scoring   — Re-rank candidates using the configured strategy
    """

    def __init__(self, strategy: SimilarityStrategy | None = None):
        self.strategy = strategy or KeywordSimilarityStrategy()

    async def find_similar(
        self,
        db: AsyncSession,
        query: str,
        limit: int = 5,
    ) -> List[ScoredCase]:
        """
        Find the top-N most similar solved cases for a given problem query.

        Phase 1: Retrieve candidates via ILIKE text search (broad net).
        Phase 2: Score each candidate and return top-N by similarity.
        """
        # Phase 1: Candidate retrieval (cast a wide net)
        candidate_limit = max(limit * 4, 20)
        candidates = await ReasoningRepository.search(db, query, limit=candidate_limit)

        if not candidates:
            logger.info("No candidate cases found for query: '%s'", query)
            return []

        # Phase 2: Score and rank
        scored = [
            ScoredCase(record=record, similarity_score=self.strategy.score(query, record))
            for record in candidates
        ]

        # Sort by similarity score descending, then confidence, then recency
        scored.sort(
            key=lambda sc: (
                sc.similarity_score,
                sc.record.confidence_score,
                sc.record.created_at,
            ),
            reverse=True,
        )

        top_results = scored[:limit]

        logger.info(
            "Case matcher for '%s': %d candidates → %d results (top score=%.3f)",
            query,
            len(candidates),
            len(top_results),
            top_results[0].similarity_score if top_results else 0.0,
        )
        return top_results
