"""
INDUS AI — IDIE v2 Recommendation Builder

Constructs the final structured recommendation containing immediate actions,
root cause analysis, supporting evidence, lessons reused, and related cases.
"""

import logging
from typing import List
from dataclasses import dataclass

from app.idie.evidence_collector import EvidenceBundle
from app.idie.decision_synthesizer import SynthesizedDecision
from app.knowledge_graph.graph_models import NodeType

logger = logging.getLogger(__name__)


@dataclass
class StructuredRecommendation:
    """Represents a fully structured cognitive recommendation."""
    immediate_actions: str
    root_cause: str
    supporting_evidence: List[str]
    lessons_reused: List[str]
    related_cases: List[str]


class RecommendationBuilder:
    """Formats and structures synthesized decisions and raw evidence for the end-user."""

    @classmethod
    def build(
        cls,
        bundle: EvidenceBundle,
        decision: SynthesizedDecision,
    ) -> StructuredRecommendation:
        """
        Builds a structured recommendation response by mapping evidence bundle fields
        and synthesized decision points.
        """
        # 1. Immediate Actions
        # Combine recommended action and any concrete solutions from factory memories
        actions_list = [decision.recommended_action]
        for mem in bundle.factory_memories[:2]:
            actions_list.append(f"Field Solution (Proven): {mem.solution}")
        
        immediate_actions = "\n\n".join(actions_list)

        # 2. Root Cause Analysis
        # Extract probable root causes based on query, RAG answer, and past cases
        root_causes = []
        if "root cause" in decision.decision_summary.lower():
            # If the LLM summary contains root cause discussion, extract or use it
            root_causes.append(decision.decision_summary)
        else:
            # Generate a structured analysis paragraph
            rag_hint = "No specific root cause identified in manuals."
            if bundle.raw_rag_response and len(bundle.raw_rag_response.answer) > 50:
                # Use the first 2 sentences of the RAG answer as a fallback hint
                sentences = bundle.raw_rag_response.answer.split(".")
                rag_hint = ". ".join(sentences[:2]) + "."
            
            past_hint = ""
            if bundle.reasoning_cases:
                past_hint = f" Past incidents of this type suggest issues: {bundle.reasoning_cases[0].problem_summary}."
            
            root_causes.append(f"Based on retrieval: {rag_hint}{past_hint}")

        root_cause = "\n\n".join(root_causes)

        # 3. Supporting Evidence
        # Combine documents used, citations, and validated factory memories
        evidence = []
        for doc in bundle.documents:
            evidence.append(f"Manual/SOP: {doc}")
        for mem in bundle.factory_memories:
            evidence.append(f"Validated Memory (Rating: {mem.rating}/5): {mem.problem[:60]}...")
        
        # Unique list
        supporting_evidence = list(dict.fromkeys(evidence))
        if not supporting_evidence:
            supporting_evidence = ["General plant standard operational guidelines."]

        # 4. Lessons Reused
        # Extract from factory memories and reasoning cases
        lessons = []
        for mem in bundle.factory_memories:
            if mem.lesson and mem.lesson.strip():
                lessons.append(f"Engineer Lesson: {mem.lesson}")
        for case in bundle.reasoning_cases:
            if case.reusable_lesson and case.reusable_lesson.strip():
                lessons.append(f"CBR Case Lesson: {case.reusable_lesson}")
        
        lessons_reused = list(dict.fromkeys(lessons))[:5]  # Top 5 unique lessons
        if not lessons_reused:
            lessons_reused = ["None matched from living memory. Standard procedures apply."]

        # 5. Related Cases
        # Extract neighbor Decision Cases from the knowledge graph context, plus similar cases
        cases = []
        for ent in bundle.graph_context:
            if ent.entity_type == NodeType.DECISION_CASE:
                direction_label = "outgoing connection" if ent.direction == "outgoing" else "incoming connection"
                cases.append(f"Case {ent.entity_id[:8]} ({direction_label})")
        
        for case in bundle.reasoning_cases:
            cases.append(f"Case {str(case.decision_case_id)[:8]} (Similarity: {case.similarity_score:.0%})")

        related_cases = list(dict.fromkeys(cases))[:5]  # Top 5 unique related cases
        if not related_cases:
            related_cases = ["No related case history linked in the knowledge graph."]

        logger.info(
            "Recommendation built with %d evidence nodes, %d lessons, %d related cases",
            len(supporting_evidence), len(lessons_reused), len(related_cases)
        )

        return StructuredRecommendation(
            immediate_actions=immediate_actions,
            root_cause=root_cause,
            supporting_evidence=supporting_evidence,
            lessons_reused=lessons_reused,
            related_cases=related_cases
        )
