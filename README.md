# INDUS AI - Living Factory Brain

INDUS AI is an Industrial Cognitive Memory System that helps factories preserve, search, connect, and continuously improve industrial knowledge from documents, maintenance records, engineer feedback, SOPs, incidents, and compliance data.

##Website URL
https://indus-ai-frontend.onrender.com

## Tech Stack
- **Frontend**: React + Vite + Tailwind CSS
- **Backend**: FastAPI
- **Database**: PostgreSQL
- **Vector Store**: FAISS
- **AI Framework**: LangChain + LangGraph
- **Authentication**: JWT + Role-Based Access Control

## Project Structure
- `/frontend`: React app powered by Vite and styled with Tailwind CSS.
- `/backend`: FastAPI Python server containing the core AI logic, database interactions, and API routes.
- `/docs`: Architecture and system documentation.
- `/sample_data`: Directory for sample industrial data used for initial indexing and RAG testing.

## Setup Steps

### Frontend
1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run the development server: `npm run dev`

### Backend
1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`

#### Database Setup & Migrations
INDUS AI uses PostgreSQL and Alembic for migrations.

1. **Install PostgreSQL**: Ensure PostgreSQL is installed and running on your system.
2. **Environment Variables**: Create a `.env` file in the `backend` directory based on the following template:
   ```env
   APP_ENV=development
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=indus_ai
   DB_USER=postgres
   DB_PASSWORD=your_password
   SECRET_KEY=your_jwt_secret
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```
3. **Run Migrations**: Apply the latest database schema:
   ```bash
   python scripts/upgrade_database.py
   ```
   *(Alternatively, run `alembic upgrade head` from the `backend` directory)*

#### Running the Backend
Use the provided script to start the development server:
```bash
python scripts/start_dev.py
```
*(Alternatively, run `uvicorn app.main:app --reload`)*

#### Alembic Migration Workflow
When you make changes to SQLAlchemy models in `app/models/`:
1. **Create a migration script**:
   ```bash
   python scripts/create_migration.py "Description of changes"
   ```
2. **Apply the migration**:
   ```bash
   python scripts/upgrade_database.py
   ```
3. **Reset Database (Dev Only)**:
   ```bash
   python scripts/reset_database.py
   ```
