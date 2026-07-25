# Enterprise Demo Dataset Seeder

This folder contains scripts to seed and clear realistic industrial demo data for the INDUS AI project.

## How to Seed Demo Data

To populate the database with realistic machines, decision cases, factory memories, incidents, SOPs, and knowledge graph edges, run:

```bash
python seed_database.py
```

This will generate exactly:
- 30 Industrial Machines
- 80 SOP Documents
- 100 Maintenance Records
- 50 Incident Reports
- 120 Engineer Insights
- 100 Factory Memory Records
- 50 Decision Cases (with AI responses, confidences, and approvals)
- 40 Reasoning Memory Records
- 200 Knowledge Graph Relationships
- 20 Compliance Violations
- 30 Generated Reports

**Important:** The demo data is never loaded automatically. It keeps the production database clean and must be executed manually.

## How to Clear Demo Data

To safely remove all generated demo data without affecting organic records, run:

```bash
python clear_demo_data.py
```

This script will trace the demo users (`demo_engineer@indus.ai`, `demo_manager@indus.ai`) and demo machines (manufactured by `INDUS Demo Corp`), cascading the deletion securely.
