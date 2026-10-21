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
- **Step 3 — Industry-Specific Questionnaire Engine**: Completed (Dynamic Questionnaire Registry for Restaurant and E-commerce, `questionnaire_responses` table, multi-step onboarding wizard).
- **Step 4 — Data Engineering Foundation**: **Completed & Verified** (Ingestion $\rightarrow$ Cleaning $\rightarrow$ Normalization $\rightarrow$ Feature Engineering $\rightarrow$ Data Quality Pipeline).
- **Step 5 — Deterministic Business Health Score Formula**: Upcoming.

---

## Data Engineering Architecture (`data-engine/`)

The **Data Engine** processes raw persisted business profiles and questionnaire metrics into validated, normalized analytical features ready for deterministic scoring:

$$\text{Persisted Data} \longrightarrow \text{Ingestion} \longrightarrow \text{Cleaning \& Validation} \longrightarrow \text{Normalization} \longrightarrow \text{Feature Engineering} \longrightarrow \text{Structured Pipeline Output}$$

```
data-engine/
├── ingestion/    # Stage 1: Data extraction from DB repositories or in-memory records
├── cleaning/     # Stage 2: Type validation, range checks, percentage bounds, outlier flags
├── features/     # Stage 3: Domain-specific financial and operational feature derivation
├── analytics/    # Stage 4: Reusable mathematical calculations and safe division helpers
├── scoring/      # Stage 5: Base scoring interface (reserved strictly for Step 5)
└── pipeline.py   # Deterministic pipeline orchestrator & structured output schema
```

### Pipeline Stages

1. **Ingestion (`ingestion/`)**:
   - `DataExtractor.extract_from_db(db, business_id)`: Reuses `BusinessRepository` and `QuestionnaireRepository` without duplicating SQL queries.
   - `DataExtractor.from_records(...)`: Enables offline batch pipelines and isolated testing.
2. **Cleaning & Validation (`cleaning/`)**:
   - Validates data types, non-negative ranges, percentage bounds ($0 \le p \le 100$), and metric units.
   - Enforces reporting period compatibility (ensures monthly flows are not combined with incompatible periods).
   - Detects duplicate question IDs or incompatible industry questions.
   - **Quality Guard**: Does **not** silently replace missing values with zero. Does **not** delete valid outliers automatically.
   - Status classifications: `valid`, `missing`, `invalid`, `derived`.
3. **Normalization**:
   - Standardizes metric keys to canonical identifiers (`monthly_revenue`, `monthly_expenses`, `employee_count`).
   - Normalizes percentage scales and formats without losing numeric precision.
   - Preserves source provenance (`source_input`) for full analytical lineage.
4. **Feature Engineering (`features/`)**:
   - **Universal Features**:
     - $\text{Operating Profit} = \text{monthly\_revenue} - \text{monthly\_expenses}$
     - $\text{Operating Margin} = (\text{operating\_profit} / \text{monthly\_revenue}) \times 100$
     - $\text{Marketing Spend Ratio} = (\text{monthly\_marketing\_spend} / \text{monthly\_revenue}) \times 100$
     - $\text{Calculated AOV} = \text{monthly\_revenue} / \text{monthly\_orders}$
   - **Restaurant Features**:
     - $\text{Revenue Per Employee} = \text{monthly\_revenue} / \text{employee\_count}$
     - $\text{Revenue Per Customer} = \text{monthly\_revenue} / \text{monthly\_customers}$
     - $\text{Orders Per Customer} = \text{monthly\_orders} / \text{monthly\_customers}$
     - $\text{Revenue Per Table} = \text{monthly\_revenue} / \text{table\_count}$ (optional)
     - $\text{Labor Intensity} = \text{monthly\_customers} / \text{employee\_count}$
   - **E-commerce Features**:
     - $\text{Revenue Per Visitor} = \text{monthly\_revenue} / \text{monthly\_website\_traffic}$
     - $\text{Orders Per Visitor} = \text{monthly\_orders} / \text{monthly\_website\_traffic}$
     - $\text{CAC to AOV Ratio} = \text{customer\_acquisition\_cost} / \text{reported\_average\_order\_value}$ (optional)
     - $\text{Effective Return Impact} = \text{monthly\_revenue} \times (\text{return\_rate\_percentage} / 100)$
   - **Zero Division & Missing Inputs**: Handled safely via `safe_divide`. Status is marked as `skipped_zero_division` or `skipped_missing_input` without raising exceptions or fabricating synthetic values.
5. **Scoring Interface (`scoring/`)**:
   - Contains `BaseScoringEngine` abstract base class.
   - **Strictly reserved for Step 5**. No scoring formulas or fabricated scores are executed.

---

## Structured Pipeline Output Schema

The pipeline returns a standardized JSON-serializable output schema:

```json
{
  "business_id": "86ddd96c-4acc-41e5-bb23-ee5993a99bd0",
  "industry": "Restaurant",
  "source_metrics": { ... },
  "cleaned_metrics": {
    "monthly_revenue": {
      "metric_id": "monthly_revenue",
      "raw_value": "450000",
      "value": 450000.0,
      "data_type": "currency",
      "unit": "₹ / $",
      "period": "monthly",
      "status": "valid",
      "source_input": "questionnaire:restaurant.monthly_revenue",
      "validation_notes": []
    }
  },
  "derived_features": {
    "operating_profit": {
      "name": "operating_profit",
      "value": 135000.0,
      "unit": "₹ / $",
      "source_inputs": ["monthly_revenue", "monthly_expenses"],
      "derivation_rule": "monthly_revenue - monthly_expenses",
      "status": "computed",
      "notes": "Net monthly operating cash generated before taxes."
    }
  },
  "missing_fields": [],
  "validation_errors": [],
  "data_quality_warnings": [],
  "processing_timestamp": "2026-10-21T14:38:00.000Z",
  "pipeline_version": "0.1.0"
}
```

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
| `category` | `VARCHAR(100)` | NOT NULL | Functional category |
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

### Data Engineering & Analytics Endpoints
| Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/businesses/{id}/data-processing` | Execute data engineering pipeline and return structured features | `200 OK` / `404 Not Found` |
| `GET` | `/api/v1/businesses/{id}/data-processing` | Query data engineering output (read-only) | `200 OK` / `404 Not Found` |

---

## Local Development & Testing

### 1. Database Migrations (Alembic)
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
alembic upgrade head
```

### 2. Run Complete Automated Test Suite (35 Tests)
```powershell
cd backend
.\.venv\Scripts\pytest.exe ..\tests -v
```
Executes all 35 unit and integration tests across:
- `tests/backend/test_health.py`: System health routes
- `tests/backend/test_businesses.py`: Business registration, validation, and listing
- `tests/backend/test_questionnaires.py`: Industry definitions, range validations, and submissions
- `tests/backend/test_data_processing_api.py`: Data processing API lifecycle, read-only GET, 404 handling
- `tests/data_engine/test_pipeline.py`: Ingestion, bounds, zero division, derived formulas, and deterministic execution

### 3. Start Backend
```powershell
cd backend
uvicorn app.main:app --reload --port 8000
```
- Swagger API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Start Frontend
```powershell
cd frontend
npm run dev
```
- Business Onboarding & Diagnostic Wizard: [http://localhost:3000/onboarding](http://localhost:3000/onboarding)

---

## Limitations & Assumptions

1. **Deterministic Processing Only**: Step 4 strictly enforces data validation, cleaning, and domain feature engineering. No machine learning, NLP, Ollama, or synthetic scoring models are utilized.
2. **Scoring Formula Reservation**: The Business Health Score evaluation formula is strictly reserved for Step 5.
3. **Flow Periodicity**: Financial and operational flow metrics (revenue, expenses, orders, customer visits) assume a standard monthly cadence.
