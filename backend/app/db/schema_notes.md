# INDUS AI Database Schema Notes

## Centrality of `decision_cases`
INDUS AI operates on a Decision Case model rather than a chat-centric model. Every query or issue becomes a `decision_case`. This table acts as the central hub connecting the user who initiated the case, the machine involved, the documents retrieved, the AI responses generated, human approvals, and the comprehensive audit trail. This ensures complete context retention for every decision.

## Living Factory Memory
The `factory_memory` and `engineer_insights` tables constitute the Living Factory Memory. They capture historical states, operational anomalies, and human heuristics (tips from engineers) over time. This enables the AI to reason not just on static SOPs, but on the evolving operational reality of the factory floor.

## Knowledge Graph Connections
The `knowledge_graph_edges` table stores directional relationships between entities (e.g., `Machine A -> requires -> SOP B` or `Incident C -> related_to -> Machine A`). This facilitates graph-based reasoning, allowing the AI to traverse related concepts and discover non-obvious dependencies during a decision case.

## Audit Trail and Trust
The `audit_logs` table provides an immutable record of all system and user actions, particularly those linked to a `decision_case`. By recording exactly what data was retrieved, what the conflict engine detected, and who approved a decision, the system ensures transparency and builds operator trust.

## Confidence Scoring
The `confidence_scores` table tracks the AI's certainty for each `ai_response`. It aggregates scores from various sources (e.g., retrieval accuracy, knowledge graph validation, conflict resolution) to present a final confidence metric. Low confidence scores trigger human-in-the-loop workflows via the `approval_requests` table.

## Three Memory Architecture

**INDUS AI is not only RAG. It combines RAG + Living Factory Memory + Case-Based Reasoning.**

INDUS AI uses three complementary memory layers to provide deep, context-aware industrial intelligence:

### 1. Document Memory (RAG Layer)
Retrieves factual content from uploaded documents (SOPs, manuals, compliance standards) via FAISS vector search on `document_chunks`. This is the foundation — fast, semantic retrieval of what has been written down.

### 2. Experience Memory (Living Factory Memory)
Captures validated human engineering experience through `engineer_insights` and operational events through `factory_memory`. This layer represents knowledge that is never written in manuals — the tribal knowledge of experienced operators and engineers.

### 3. Reasoning Memory (Case-Based Reasoning)
Stored in the `reasoning_memory` table, this layer records how previous `decision_cases` were solved: the reasoning steps taken, the evidence used, which agents were involved, the final recommendation, and the outcome. When a similar problem arises, the AI can retrieve and adapt previous reasoning patterns instead of solving from scratch. The `reusable_lesson` and `success_score` fields enable the system to learn which reasoning strategies work best over time.
