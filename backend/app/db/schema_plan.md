# INDUS AI - Database Schema Plan

## Overview
This document outlines the proposed database schema for INDUS AI using PostgreSQL.

## Tables

### `users`
- `id`: UUID (Primary Key)
- `email`: String (Unique)
- `hashed_password`: String
- `role_id`: UUID (Foreign Key)
- `created_at`: Timestamp
- `updated_at`: Timestamp

### `roles`
- `id`: UUID (Primary Key)
- `name`: String (Admin, Engineer, Manager, etc.)
- `permissions`: JSON

### `documents`
- `id`: UUID (Primary Key)
- `title`: String
- `type`: String (SOP, Manual, etc.)
- `status`: String
- `uploaded_by`: UUID (Foreign Key)
- `created_at`: Timestamp

### `document_chunks`
- `id`: UUID (Primary Key)
- `document_id`: UUID (Foreign Key)
- `content`: Text
- `vector_id`: String (reference to FAISS)

### `machines`
- `id`: UUID (Primary Key)
- `name`: String
- `status`: String
- `location`: String

### `maintenance_records`
- `id`: UUID (Primary Key)
- `machine_id`: UUID (Foreign Key)
- `description`: Text
- `performed_by`: UUID (Foreign Key)
- `date`: Date

### `incidents`
- `id`: UUID (Primary Key)
- `description`: Text
- `severity`: String
- `reported_by`: UUID (Foreign Key)
- `created_at`: Timestamp

### `inspection_reports`
- `id`: UUID (Primary Key)
- `inspector_id`: UUID (Foreign Key)
- `content`: Text
- `date`: Date

### `sops`
- `id`: UUID (Primary Key)
- `document_id`: UUID (Foreign Key)
- `version`: String

### `compliance_rules`
- `id`: UUID (Primary Key)
- `rule_name`: String
- `description`: Text

### `engineer_insights`
- `id`: UUID (Primary Key)
- `engineer_id`: UUID (Foreign Key)
- `insight`: Text
- `machine_id`: UUID (Foreign Key)

### `factory_memory`
- `id`: UUID (Primary Key)
- `event_description`: Text
- `timestamp`: Timestamp

### `knowledge_graph_edges`
- `id`: UUID (Primary Key)
- `source_node`: String
- `target_node`: String
- `relation`: String

### `ai_queries`
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key)
- `query_text`: Text
- `timestamp`: Timestamp

### `ai_responses`
- `id`: UUID (Primary Key)
- `query_id`: UUID (Foreign Key)
- `response_text`: Text
- `confidence_score`: Float

### `confidence_scores`
- `id`: UUID (Primary Key)
- `response_id`: UUID (Foreign Key)
- `score`: Float

### `conflict_logs`
- `id`: UUID (Primary Key)
- `description`: Text
- `resolved`: Boolean

### `approval_requests`
- `id`: UUID (Primary Key)
- `request_details`: Text
- `status`: String (Pending, Approved, Rejected)
- `approver_id`: UUID (Foreign Key)

### `notifications`
- `id`: UUID (Primary Key)
- `user_id`: UUID (Foreign Key)
- `message`: Text
- `is_read`: Boolean
- `created_at`: Timestamp

### `generated_reports`
- `id`: UUID (Primary Key)
- `report_url`: String
- `generated_by`: UUID (Foreign Key)
- `created_at`: Timestamp

### `audit_logs`
- `id`: UUID (Primary Key)
- `action`: String
- `user_id`: UUID (Foreign Key)
- `timestamp`: Timestamp
