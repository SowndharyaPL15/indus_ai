# INDUS AI Architecture

INDUS AI is an Industrial Cognitive Memory System designed to help factories preserve, search, connect, and continuously improve industrial knowledge.

## System Architecture

**INDUS AI = RAG + Multi-Agent AI + Living Memory + Knowledge Graph + Confidence Scoring + Conflict Detection + Audit Trail + Human Approval + Notifications + Enterprise Security**

### 1. Frontend Layer
- **Tech**: React, Vite, Tailwind CSS.
- **Role**: Provides a premium industrial SaaS dashboard for interactions, knowledge retrieval, and system management.
- **Key Modules**: Knowledge Copilot, Maintenance Intelligence, Document Upload, Compliance Center.

### 2. Backend Layer
- **Tech**: FastAPI, Python.
- **Role**: Core orchestration, API serving, and business logic execution.
- **Key Modules**: Authentication (JWT, RBAC), REST APIs.

### 3. AI & Cognitive Layer
- **Tech**: LangChain, LangGraph, FAISS, Sentence Transformers.
- **Role**: Powers the 'Living Factory Brain'. Connects structured and unstructured data.
- **Key Features**:
  - **RAG**: Retrieval-Augmented Generation for document insights.
  - **Multi-Agent System**: Specialized agents for maintenance, compliance, and general queries.
  - **Living Memory**: Continuously updated repository of engineer insights and factory events.
  - **Knowledge Graph**: Relationship mapping between entities (machines, incidents, docs).
  - **Confidence Scoring & Conflict Detection**: Ensures reliability of AI responses.

### 4. Data Layer
- **Tech**: PostgreSQL.
- **Role**: Persistent storage for users, machines, maintenance records, and audit logs.

### 5. Security & Governance Layer
- **Role**: Ensure enterprise-grade security.
- **Key Features**: Human approval workflows, Audit trails for all actions, Role-Based Access Control.
