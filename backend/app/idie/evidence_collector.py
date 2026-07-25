"""
INDUS AI — IDIE v2 Evidence Collector

Collects evidence from all four factory knowledge sources:
1. RAG Documents
2. Living Factory Memory
3. Similar Reasoning Cases
4. Knowledge Graph Context
"""

import time
import logging
from typing import List, Dict, Optional
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

# Service & component imports
from app.rag.retrieval.query_pipeline import process_query
from app.schemas.copilot import QueryResponse, Citation
from app.models.factory_memory_record import FactoryMemoryRecord
from app.memory_engine.memory_retriever import MemoryRetriever
from app.reasoning_engine.reasoning_service import ReasoningService
from app.reasoning_engine.reasoning_models import SimilarCasesResponse, SimilarCaseResult
from app.knowledge_graph.graph_service import GraphService
from app.knowledge_graph.graph_models import CaseContextResponse, ConnectedEntity

logger = logging.getLogger(__name__)


@dataclass
class EvidenceBundle:
    """Contains all raw and parsed evidence gathered from the factory knowledge base."""
    query: str
    decision_case_id: str
    documents: List[str]
    citations: List[Citation]
    factory_memories: List[FactoryMemoryRecord]
    reasoning_cases: List[SimilarCaseResult]
    graph_context: List[ConnectedEntity]
    processing_times: Dict[str, float]
    raw_rag_response: Optional[QueryResponse] = None


class EvidenceCollector:
    """Orchestrates gathering of evidence across RAG, Memory, Reasoning, and Graph systems."""

    @classmethod
    async def collect_all(
        cls,
        db: AsyncSession,
        query: str,
        decision_case_id: str,
    ) -> EvidenceBundle:
        """
        Gathers evidence from all 4 systems in a parallel-safe (try-except isolated) sequence.
        Measures individual timings.
        """
        timings = {}
        
        # 1. Collect Documents (RAG)
        t_start = time.time()
        rag_res = None
        docs = []
        cits = []
        try:
            rag_res = await cls.collect_documents(db, query)
            docs = rag_res.documents_used
            cits = rag_res.citations
        except Exception as e:
            logger.error("Failed to collect RAG documents: %s", str(e), exc_info=True)
        timings["rag"] = time.time() - t_start

        # 2. Collect Factory Memory
        t_start = time.time()
        memories = []
        try:
            memories = await cls.collect_factory_memory(db, query)
        except Exception as e:
            logger.error("Failed to collect Factory Memory: %s", str(e), exc_info=True)
        timings["factory_memory"] = time.time() - t_start

        # 3. Collect Similar Reasoning Cases
        t_start = time.time()
        cases = []
        try:
            cases_res = await cls.collect_reasoning_cases(db, query)
            cases = cases_res.results
        except Exception as e:
            logger.error("Failed to collect Similar Reasoning Cases: %s", str(e), exc_info=True)
        timings["reasoning"] = time.time() - t_start

        # 4. Collect Knowledge Graph Context
        t_start = time.time()
        graph_entities = []
        try:
            graph_res = await cls.collect_graph_context(db, decision_case_id)
            # Flatten the groups to a simple list of ConnectedEntity for the bundle
            for group in graph_res.groups:
                graph_entities.extend(group.entities)
        except Exception as e:
            logger.error("Failed to collect Knowledge Graph context: %s", str(e), exc_info=True)
        timings["knowledge_graph"] = time.time() - t_start

        logger.info(
            "Evidence collection complete for query '%s' [Docs: %d, Memory: %d, Cases: %d, Graph: %d]",
            query[:40], len(docs), len(memories), len(cases), len(graph_entities)
        )

        return EvidenceBundle(
            query=query,
            decision_case_id=decision_case_id,
            documents=docs,
            citations=cits,
            factory_memories=memories,
            reasoning_cases=cases,
            graph_context=graph_entities,
            processing_times=timings,
            raw_rag_response=rag_res
        )

    @staticmethod
    async def collect_documents(db: AsyncSession, query: str) -> QueryResponse:
        """Query the RAG pipeline."""
        return await process_query(db, query)

    @staticmethod
    async def collect_factory_memory(db: AsyncSession, query: str) -> List[FactoryMemoryRecord]:
        """Query living factory memories."""
        return await MemoryRetriever.get_relevant_memories(db, query, limit=5)

    @staticmethod
    async def collect_reasoning_cases(db: AsyncSession, query: str) -> SimilarCasesResponse:
        """Query Reasoning Case-Based Reasoning records."""
        return await ReasoningService.get_similar_cases(db, query, limit=5)

    @staticmethod
    async def collect_graph_context(db: AsyncSession, decision_case_id: str) -> CaseContextResponse:
        """Query the Knowledge Graph context for the current decision case."""
        return await GraphService.get_case_context(db, decision_case_id)
