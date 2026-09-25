# Stanleaf — Business Health Intelligence Platform

> **"Business Intelligence, Simplified."**

**Stanleaf** is a startup-grade Business Health Intelligence platform designed to analyze small, medium, and growing enterprises using public market data and owner-provided financial and operational metrics. 

The platform calculates an **explainable Business Health Score**, benchmarks organizations against comparable industry cohorts, identifies operational risks, predicts financial trends, and surfaces actionable management recommendations.

---

## Capstone Academic Specialization

Stanleaf is architected as a Computer Science Engineering (CSE) final-year capstone project specializing in **Data Science and Big Data Analytics**. 

The architecture strictly separates concerns:
- **Presentation Layer**: Next.js App Router, Tailwind CSS, TypeScript.
- **API & Domain Layer**: FastAPI, Pydantic v2, SQLAlchemy 2.0, Repository pattern.
- **Persistence Layer**: PostgreSQL relational database with versioned Alembic migrations.
- **Data Science & Big Data Layer (`data-engine/`)**: Ingestion adapters, data cleaning, feature stores, cohort analytics, and deterministic scoring models.
- **Machine Learning Layer (`ml/`)**: Model training, serializations, and SHAP explainability.
- **Local AI & NLP Layer (`ai/`)**: Self-hosted Ollama for local qualitative insights.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | [Next.js](https://nextjs.org/) (v14+ App Router), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/), [Lucide React](https://lucide.dev/) |
| **Backend** | [Python 3.12](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [Pydantic v2](https://docs.pydantic.dev/) |
| **Database & ORM** | [PostgreSQL 16](https://www.postgresql.org/), [SQLAlchemy 2.0](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/) |
| **Data Engine & Analytics** | Python, [Pandas](https://pandas.pydata.org/) / [Polars](https://pola.rs/), [NumPy](https://numpy.org/) |
| **Machine Learning** | [Scikit-learn](https://scikit-learn.org/), [XGBoost](https://xgboost.readthedocs.io/), [SHAP](https://shap.readthedocs.io/) |
| **Local AI & NLP** | [Ollama](https://ollama.ai/) (Llama 3.1), [Hugging Face Transformers](https://huggingface.co/) |
| **Infrastructure** | Docker, Docker Compose, Git, Pytest |

---

## Repository Architecture

```
stanleaf/
├── frontend/                     # Next.js 14 App Router + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── app/                  # App Router pages (/, /onboarding), layout, styles
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx        # Responsive root layout with Header & Footer
│   │   │   ├── page.tsx          # Landing hero page + status indicator
│   │   │   └── onboarding/
│   │   │       └── page.tsx      # Business Onboarding form & success state
│   │   ├── components/           # Header, Footer, HealthStatusBadge, ArchitectureCard
│   │   └── lib/                  # API client (Health & Business CRUD methods)
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.mjs
│   ├── .env.example
│   └── .gitignore
│
├── backend/                      # Python FastAPI asynchronous backend
│   ├── alembic/                  # Database migration management
│   │   ├── env.py                # Dynamic configuration & Base.metadata binding
│   │   └── versions/             # Versioned schema migrations
│   │       └── 001_create_businesses_table.py
│   ├── app/
│   │   ├── api/v1/               # Versioned REST API endpoints
│   │   │   ├── endpoints/
│   │   │   │   ├── health.py     # Health check API
│   │   │   │   └── businesses.py # Business registration & query endpoints
│   │   │   └── router.py         # Aggregated v1 routing table
│   │   ├── core/
│   │   │   ├── config.py         # Type-safe configuration via Pydantic Settings
│   │   │   ├── cors.py           # CORS policies allowing frontend communication
│   │   │   └── database.py       # SQLAlchemy engine, SessionLocal, get_db()
│   │   ├── models/               # SQLAlchemy ORM models
│   │   │   └── business.py       # Business entity table definition
│   │   ├── repositories/         # Data access repository layer
│   │   │   └── business.py       # Encapsulated Business CRUD operations
│   │   ├── schemas/              # Pydantic validation & response schemas
│   │   │   └── business.py       # BusinessBase, BusinessCreate, BusinessResponse
│   │   └── main.py               # FastAPI application lifecycle and entrypoint
│   ├── requirements.txt          # Python backend dependencies
│   ├── alembic.ini               # Alembic configuration
│   ├── .env.example
│   └── .gitignore
│
├── data-engine/                  # Data Science & Big Data Analytics Layer
│   ├── ingestion/                # External data adapters & upload schemas
│   ├── cleaning/                 # Data deduplication, sanitization, and imputation
│   ├── features/                 # Financial ratios, operational velocity features
│   ├── analytics/                # Cohort aggregation, statistical distributions
│   └── scoring/                  # Mathematical explainable health score formula
│
├── ml/                           # Machine Learning Layer (scikit-learn, XGBoost)
│   ├── models/                   # Model registry and serialized artifacts
│   ├── training/                 # Model training pipelines
│   └── evaluation/               # Metrics tracking, validation, SHAP explainability
│
├── ai/                           # Local AI & NLP Layer (Ollama)
│   └── ollama/                   # Local LLM service config, prompt templates
│
├── database/                     # PostgreSQL storage blueprints
│   ├── schema/                   # PostgreSQL DDL schemas
│   │   └── 001_initial_schema.sql
│   └── migrations/               # Database migrations reference
│
├── notebooks/                    # Jupyter notebooks for EDA and prototyping
├── tests/                        # Automated testing suite
│   ├── backend/
│   │   ├── test_health.py        # Health endpoint tests
│   │   └── test_businesses.py    # Business registration & validation tests
│   └── data_engine/
│
├── docker-compose.yml            # PostgreSQL 16 container definition
├── .gitignore                    # Global git ignore configuration
├── .env.example                  # Consolidated environment variable template
└── README.md                     # Documentation & setup guide
```

---

## Database Model: Business

The core domain entity `businesses` is defined as follows:

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key, Indexed | Auto-generated unique identifier |
| `name` | `VARCHAR(255)` | NOT NULL, Indexed | Business name |
| `industry` | `VARCHAR(255)` | NOT NULL, Indexed | Industry / Sector |
| `location` | `VARCHAR(255)` | NOT NULL | City, Country, or Region |
| `website` | `VARCHAR(500)` | Nullable | Validated URL format |
| `business_age_years` | `INT` | Nullable, $\ge 0$ | Operating age in years |
| `revenue_range` | `VARCHAR(100)` | Nullable | Revenue bracket |
| `employee_count` | `INT` | Nullable, $\ge 0$ | Total headcount |
| `customer_count` | `INT` | Nullable, $\ge 0$ | Active customer count |
| `marketing_spend_monthly` | `FLOAT` | Nullable, $\ge 0$ | Monthly marketing expenditure |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, Default `now()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, Default `now()` | Auto-updated modification timestamp |

---

## API Endpoints

### Business Endpoints

| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/businesses` | Register and persist a new business | `201 Created` |
| `GET` | `/api/v1/businesses` | List registered businesses (paginated) | `200 OK` |
| `GET` | `/api/v1/businesses/{id}` | Get business details by UUID | `200 OK` / `404 Not Found` |

#### Example Business Creation Request:
`POST /api/v1/businesses`
```json
{
  "name": "Apex Health Technologies",
  "industry": "Healthcare & MedTech",
  "location": "Bengaluru, India",
  "website": "https://apexhealth.io",
  "business_age_years": 4,
  "revenue_range": "25L-50L",
  "employee_count": 28,
  "customer_count": 5200,
  "marketing_spend_monthly": 65000.0
}
```

#### Example Business Creation Response:
`201 Created`
```json
{
  "id": "e4a3c18b-6c48-4cb9-b8fb-8c34dc4391cb",
  "name": "Apex Health Technologies",
  "industry": "Healthcare & MedTech",
  "location": "Bengaluru, India",
  "website": "https://apexhealth.io",
  "business_age_years": 4,
  "revenue_range": "25L-50L",
  "employee_count": 28,
  "customer_count": 5200,
  "marketing_spend_monthly": 65000.0,
  "created_at": "2026-09-25T12:00:00.000000Z",
  "updated_at": "2026-09-25T12:00:00.000000Z"
}
```

---

## Local Development Setup

### Prerequisites
- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher
- **Python**: v3.10 or higher
- **PostgreSQL**: Local service or Docker

---

### 1. Database Setup (PostgreSQL)

You can run PostgreSQL either via **Docker Compose** or via a **local PostgreSQL installation**:

#### Option A: Run via Docker Compose
```bash
docker compose up -d postgres
```
This spins up PostgreSQL on port `5432` with database `stanleaf`, user `stanleaf`, password `stanleaf`.

#### Option B: Local PostgreSQL Service
Create the database and user using `psql`:
```sql
CREATE USER stanleaf WITH PASSWORD 'stanleaf';
CREATE DATABASE stanleaf OWNER stanleaf;
```

---

### 2. Run Database Migrations (Alembic)

Navigate to the `backend/` directory:
```bash
cd backend
.\.venv\Scripts\Activate.ps1   # On Windows
# source .venv/bin/activate    # On macOS/Linux

alembic upgrade head
```

To rollback a migration:
```bash
alembic downgrade -1
```

---

### 3. Start the FastAPI Backend

From `backend/`:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Health Check: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- Swagger Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc Documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 4. Start the Next.js Frontend

Open a new terminal and navigate to `frontend/`:
```bash
cd frontend
npm install
npm run dev
```
- Homepage: [http://localhost:3000](http://localhost:3000)
- Business Onboarding: [http://localhost:3000/onboarding](http://localhost:3000/onboarding)

---

### 5. Running Automated Tests

Run the complete automated backend test suite using Pytest:

```powershell
cd backend
.\.venv\Scripts\pytest.exe ..\tests\backend -v
```

The test suite runs against an isolated in-memory test database strategy and verifies:
1. `test_create_valid_business`: 201 Created with valid UUID and timestamp persistence.
2. `test_reject_invalid_business_data`: 422 Unprocessable Entity on missing/empty fields, negative numbers, and invalid URLs.
3. `test_retrieve_business`: 200 OK on retrieving a business by ID.
4. `test_retrieve_nonexistent_business_404`: 404 Not Found for non-existent UUIDs.
5. `test_list_businesses`: 200 OK returning all registered business records.
6. `test_health_endpoint_v1`, `test_health_endpoint_convenience`, `test_root_endpoint`.
