# Stanleaf — Business Health Intelligence Platform

> **"Business Intelligence, Simplified."**

**Stanleaf** is a startup-grade Business Health Intelligence platform designed to analyze small, medium, and growing enterprises using public market data and owner-provided financial and operational metrics. 

The platform calculates an **explainable Business Health Score**, benchmarks organizations against comparable industry cohorts, identifies operational risks, predicts financial trends, and surfaces actionable management recommendations.

---

## Capstone Academic Specialization

Stanleaf is architected as a Computer Science Engineering (CSE) final-year capstone project specializing in **Data Science and Big Data Analytics**. 

The architecture strictly separates concerns:
- **Presentation Layer**: Next.js App Router, Tailwind CSS, TypeScript (Dynamic Form Wizards).
- **API & Domain Layer**: FastAPI, Pydantic v2, SQLAlchemy 2.0, Repository and Service Patterns.
- **Persistence Layer**: PostgreSQL relational database with versioned Alembic migrations.
- **Questionnaire & Ingestion Layer**: Industry-specific diagnostic collection layer preparing structured inputs for analytical feature stores.
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

## Current Development Stage

- **Step 1 — Foundation**: Completed (Next.js, FastAPI, CORS, Health Check, Docker configuration).
- **Step 2 — Business Onboarding + Database**: Completed (PostgreSQL, SQLAlchemy, Alembic, Repository Pattern, Business Model).
- **Step 3 — Industry-Specific Questionnaire Engine**: **Completed & Verified** (Dynamic Questionnaire Registry for Restaurant and E-commerce, `questionnaire_responses` table, multi-step onboarding wizard).
- **Step 4 — Data Engine Foundation (Upcoming)**: Ingestion $\rightarrow$ Cleaning $\rightarrow$ Normalization $\rightarrow$ Feature Engineering $\rightarrow$ Data Quality.

---

## Questionnaire Engine Architecture

The Questionnaire Engine serves as the structured data-collection gateway feeding the future Data Science and Analytics layer:

$$\text{Business Profile} \longrightarrow \text{Industry} \longrightarrow \text{Industry Questionnaire} \longrightarrow \text{Validated Responses} \longrightarrow \text{Structured Business Data} \longrightarrow \text{Data Science / ML}$$

### Supported Industries Initially
1. **Restaurant (`restaurant`)**: 12 diagnostic questions across Financial, Customer, Operations, Marketing, and Reputation.
2. **E-commerce (`ecommerce`)**: 11 diagnostic questions across Financial, Customer, Operations, Marketing, and Growth.

### Extensible Registry
Questionnaire definitions reside as Python configuration schemas in `backend/app/services/questionnaire_definitions/`. Adding new industries (e.g. Healthcare, Retail, Logistics) requires only adding a new definition module without altering the database schema.

---

## Database Schemas

### 1. `businesses` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key, Indexed | Auto-generated UUID |
| `name` | `VARCHAR(255)` | NOT NULL, Indexed | Business name |
| `industry` | `VARCHAR(255)` | NOT NULL, Indexed | Industry / Sector |
| `location` | `VARCHAR(255)` | NOT NULL | Operating location |
| `website` | `VARCHAR(500)` | Nullable | Validated URL |
| `business_age_years` | `INT` | Nullable, $\ge 0$ | Age in years |
| `revenue_range` | `VARCHAR(100)` | Nullable | Revenue bracket |
| `employee_count` | `INT` | Nullable, $\ge 0$ | Total headcount |
| `customer_count` | `INT` | Nullable, $\ge 0$ | Active customers |
| `marketing_spend_monthly` | `FLOAT` | Nullable, $\ge 0$ | Monthly marketing spend |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, `now()` | Record creation timestamp |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, `now()` | Record update timestamp |

### 2. `questionnaire_responses` Table
| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `UUID` | Primary Key, Indexed | Auto-generated UUID |
| `business_id` | `UUID` | Foreign Key (`businesses.id`), Indexed | Linked business entity |
| `question_id` | `VARCHAR(100)` | NOT NULL, Indexed | Stable question identifier |
| `industry` | `VARCHAR(100)` | NOT NULL, Indexed | Industry key (e.g. `restaurant`) |
| `category` | `VARCHAR(100)` | NOT NULL | Functional category (Financial, Operations, etc.) |
| `value` | `TEXT` | NOT NULL | Raw string representation |
| `numeric_value` | `FLOAT` | Nullable | Parsed numerical value for analytical modeling |
| `data_type` | `VARCHAR(50)` | NOT NULL | Data type (`currency`, `percentage`, etc.) |
| `unit` | `VARCHAR(50)` | Nullable | Measurement unit (`₹ / $`, `%`, `stars`, etc.) |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, `now()` | Timestamp |
| `updated_at` | `TIMESTAMPTZ` | NOT NULL, `now()` | Timestamp |

*Constraint:* `UNIQUE(business_id, question_id)` guarantees idempotent updates per question.

---

## API Endpoints

### System & Health Endpoints
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Live system health and metadata |

### Business Endpoints
| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/businesses` | Register a new business | `201 Created` / `422 Unprocessable Content` |
| `GET` | `/api/v1/businesses` | List registered businesses | `200 OK` |
| `GET` | `/api/v1/businesses/{id}` | Get business details by UUID | `200 OK` / `404 Not Found` |

### Questionnaire Endpoints
| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/questionnaires/{industry}` | Retrieve diagnostic question definitions | `200 OK` / `404 Not Found` |
| `POST` | `/api/v1/businesses/{id}/questionnaire` | Submit and validate questionnaire answers | `201 Created` / `422 Unprocessable Content` |
| `GET` | `/api/v1/businesses/{id}/questionnaire` | Retrieve stored questionnaire responses | `200 OK` / `404 Not Found` |

---

## Local Development & Testing

### 1. Database Migrations (Alembic)
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

### 2. Run Automated Pytest Suite
```powershell
pytest ..\tests\backend -v
```
Runs 18 unit and integration tests across health endpoints, business models, and questionnaire validations in < 1 second.

### 3. Start Backend
```powershell
uvicorn app.main:app --reload --port 8000
```
- Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Start Frontend
```powershell
cd frontend
npm run dev
```
- Business Onboarding & Diagnostic Wizard: [http://localhost:3000/onboarding](http://localhost:3000/onboarding)
