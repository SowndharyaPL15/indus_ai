"""
INDUS AI — IDIE v2 Decision Synthesizer

Synthesizes the ranked and grouped evidence bundle into structured decision components
using the central LLM service, with a robust rule-based programmatic fallback.
"""

import logging
from typing import List
from dataclasses import dataclass

from langchain_core.prompts import ChatPromptTemplate
from app.rag.llm_service import get_llm
from app.idie.evidence_collector import EvidenceBundle

logger = logging.getLogger(__name__)


@dataclass
class SynthesizedDecision:
    """Represents the synthesized intelligence before building the final recommendation response."""
    decision_summary: str
    evidence_used: List[str]
    key_risks: List[str]
    recommended_action: str
    alternative_actions: List[str]


class DecisionSynthesizer:
    """Fuses raw evidence across RAG, Memory, CBR, and Graph systems into high-quality decision points."""

    @classmethod
    async def synthesize(
        cls,
        bundle: EvidenceBundle,
    ) -> SynthesizedDecision:
        """
        Synthesize the collected evidence bundle.
        Attempts to use the RAG LLM for a high-quality summary and risk synthesis.
        Falls back to programmatic generation if the LLM fails or is unconfigured.
        """
        # Determine evidence sources used
        evidence_used = []
        if bundle.raw_rag_response and bundle.raw_rag_response.documents_used:
            evidence_used.append("Documents (RAG)")
        if bundle.factory_memories:
            evidence_used.append("Living Factory Memory")
        if bundle.reasoning_cases:
            evidence_used.append("Reasoning Memory (CBR)")
        if bundle.graph_context:
            evidence_used.append("Knowledge Graph Context")

        # Format context for LLM
        rag_answer = bundle.raw_rag_response.answer if bundle.raw_rag_response else "No RAG information found."
        
        mem_lines = []
        for i, m in enumerate(bundle.factory_memories, 1):
            mem_lines.append(f"Memory #{i}: Problem: {m.problem} | Solution: {m.solution} | Lesson: {m.lesson}")
        memories_text = "\n".join(mem_lines) if mem_lines else "No Living Factory Memories found."

        case_lines = []
        for i, c in enumerate(bundle.reasoning_cases, 1):
            case_lines.append(
                f"Case #{i} ({c.outcome_status}): Title: {c.case_title} | Problem: {c.problem_summary} | "
                f"Recommendation: {c.final_recommendation} | Lesson: {c.reusable_lesson or ''}"
            )
        cases_text = "\n".join(case_lines) if case_lines else "No similar reasoning cases found."

        graph_lines = []
        for i, e in enumerate(bundle.graph_context, 1):
            graph_lines.append(f"Entity: {e.entity_type} ID: {e.entity_id} Relationship: {e.relationship_type}")
        graph_text = "\n".join(graph_lines) if graph_lines else "No related graph connections found."

        prompt_text = (
            "You are the Decision Intelligence synthesis engine for INDUS AI.\n"
            "Given the user query, combine all of the following evidence sources to produce a structured synthesis.\n\n"
            f"Query: {bundle.query}\n\n"
            f"1. RAG Answer: {rag_answer}\n\n"
            f"2. Living Factory Memories:\n{memories_text}\n\n"
            f"3. Similar Reasoning Cases:\n{cases_text}\n\n"
            f"4. Related Graph Context:\n{graph_text}\n\n"
            "Generate the following parts, and separate each section with these tags exactly:\n"
            "[SUMMARY]\n(A clear unified summary combining RAG, memory insights, and past case outcomes)\n"
            "[RECOMMENDED_ACTION]\n(Clear, actionable recommendation based on what was proven to work)\n"
            "[RISKS]\n(Any key risks identified, especially from failed or partially successful past cases, or general safety concerns)\n"
            "[ALTERNATIVES]\n(One or two alternative actions if the primary recommendation isn't viable or needs fallback options. List as bullet points)\n"
        )

        try:
            llm = get_llm()
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a professional industrial cognitive advisor. Be precise, concise, and structured."),
                ("human", "{prompt_text}")
            ])
            chain = prompt | llm
            response = await chain.ainvoke({"prompt_text": prompt_text})
            content = response.content

            # Parse tags
            summary = cls._extract_section(content, "[SUMMARY]", ["[RECOMMENDED_ACTION]", "[RISKS]", "[ALTERNATIVES]"])
            rec_action = cls._extract_section(content, "[RECOMMENDED_ACTION]", ["[SUMMARY]", "[RISKS]", "[ALTERNATIVES]"])
            risks_raw = cls._extract_section(content, "[RISKS]", ["[SUMMARY]", "[RECOMMENDED_ACTION]", "[ALTERNATIVES]"])
            alts_raw = cls._extract_section(content, "[ALTERNATIVES]", ["[SUMMARY]", "[RECOMMENDED_ACTION]", "[RISKS]"])

            # Clean and split lists
            key_risks = [line.strip("- *").strip() for line in risks_raw.split("\n") if line.strip()]
            alt_actions = [line.strip("- *").strip() for line in alts_raw.split("\n") if line.strip()]

            # Fallback values if sections are blank
            if not summary:
                summary = f"Synthesized analysis for query: {bundle.query}. Combined inputs from {', '.join(evidence_used)}."
            if not rec_action:
                rec_action = rag_answer

            return SynthesizedDecision(
                decision_summary=summary,
                evidence_used=evidence_used,
                key_risks=key_risks or ["No significant risks identified."],
                recommended_action=rec_action,
                alternative_actions=alt_actions or ["Follow standard SOP protocols."]
            )

        except Exception as e:
            logger.warning("LLM Synthesis failed, using fallback synthesizer: %s", str(e))
            return cls._fallback_synthesis(bundle, evidence_used, rag_answer)

    @staticmethod
    def _extract_section(text: str, tag: str, next_tags: List[str]) -> str:
        """Helper to extract tag-delimited text sections."""
        if tag not in text:
            return ""
        start_idx = text.find(tag) + len(tag)
        end_idx = len(text)

        for next_tag in next_tags:
            idx = text.find(next_tag)
            if idx != -1 and idx > start_idx:
                end_idx = min(end_idx, idx)

        return text[start_idx:end_idx].strip()

    @classmethod
    def _fallback_synthesis(
        cls,
        bundle: EvidenceBundle,
        evidence_used: List[str],
        rag_answer: str,
    ) -> SynthesizedDecision:
        """Fallback rule-based synthesizer when LLM service is offline."""
        summary = (
            f"Fusing knowledge base context to address: '{bundle.query}'. "
            f"Retrieved {len(bundle.factory_memories)} living factory memories and "
            f"{len(bundle.reasoning_cases)} similar historical cases. "
            f"Primary RAG answer: {rag_answer[:150]}..."
        )

        key_risks = []
        for c in bundle.reasoning_cases:
            if c.outcome_status in ["FAILED", "PARTIALLY_SUCCESSFUL"]:
                key_risks.append(f"Risk identified from historical failure (Case ID: {c.decision_case_id[:8]}): {c.final_recommendation[:100]}")
        
        if not key_risks:
            key_risks.append("No specific historical case failures match this incident.")

        alt_actions = []
        for m in bundle.factory_memories:
            alt_actions.append(f"Re-use engineer solution: {m.solution[:150]}")
        for c in bundle.reasoning_cases:
            if c.outcome_status == "SUCCESSFUL":
                alt_actions.append(f"Apply CBR recommendation: {c.final_recommendation[:150]}")

        # Limit alternatives
        alt_actions = alt_actions[:3]
        if not alt_actions:
            alt_actions.append("Reference machine operating manuals and standard SOPs.")

        return SynthesizedDecision(
            decision_summary=summary,
            evidence_used=evidence_used,
            key_risks=key_risks,
            recommended_action=rag_answer,
            alternative_actions=alt_actions
        )
