# Stanleaf — Business Health Intelligence Platform

> **"Business Intelligence, Simplified."**

**Stanleaf** is a startup-grade Business Health Intelligence platform designed to analyze small, medium, and growing enterprises using public registry/market data and owner-provided financial and operational metrics. 

The platform calculates an **explainable Business Health Score**, benchmarks organizations against comparable industry cohorts, identifies operational risks, predicts financial trends, and surfaces actionable management recommendations.

---

## Capstone Academic Specialization

Stanleaf is architected as a Computer Science Engineering (CSE) final-year capstone project specializing in **Data Science and Big Data Analytics**. 

To satisfy rigorous academic and software engineering standards, the architecture strictly separates the **Data Science & Analytics Engine** from the web API backend, database, and presentation layers. Data ingestion, wrangling, feature engineering, statistical cohort benchmarking, and deterministic scoring models are completely decoupled from UI and network transport concerns.

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | [Next.js](https://nextjs.org/) (v14+ App Router), [TypeScript](https://www.typescriptlang.org/), [Tailwind CSS](https://tailwindcss.com/), [Lucide React](https://lucide.dev/) |
| **Backend** | [Python 3.12](https://www.python.org/), [FastAPI](https://fastapi.tiangolo.com/), [Uvicorn](https://www.uvicorn.org/), [Pydantic v2](https://docs.pydantic.dev/) |
| **Data Engine & Analytics** | Python, [Pandas](https://pandas.pydata.org/) / [Polars](https://pola.rs/), [NumPy](https://numpy.org/) |
| **Machine Learning** | [Scikit-learn](https://scikit-learn.org/), [XGBoost](https://xgboost.readthedocs.io/), [SHAP](https://shap.readthedocs.io/) |
| **Local AI & NLP** | [Ollama](https://ollama.ai/) (Llama 3.1), [Hugging Face Transformers](https://huggingface.co/) |
| **Database** | [PostgreSQL](https://www.postgresql.org/) (Relational Core, Time-Series & Cohort Indices) |
| **Infrastructure** | Docker, Git, Pytest |

---

## Repository Architecture

```
stanleaf/
├── frontend/                     # Next.js 14 App Router + TypeScript + Tailwind CSS
│   ├── src/
│   │   ├── app/                  # App Router pages, layout, and global CSS
│   │   │   ├── globals.css
│   │   │   ├── layout.tsx        # Responsive root layout with Header & Footer
│   │   │   └── page.tsx          # Hero page, status check, architectural pillars
│   │   ├── components/           # Modular UI components (Header, Footer, Badges, Cards)
│   │   └── lib/                  # API client, TypeScript interfaces, and utilities
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.ts
│   ├── postcss.config.mjs
│   ├── .env.example
│   └── .gitignore
│
├── backend/                      # Python FastAPI asynchronous backend
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/               # Versioned API endpoints
│   │   │       ├── endpoints/
│   │   │       │   └── health.py # Health check API with system metadata
│   │   │       └── router.py     # Aggregated v1 routing table
│   │   ├── core/
│   │   │   ├── config.py         # Type-safe configuration via Pydantic Settings
│   │   │   └── cors.py           # Configured CORS middleware for frontend communication
│   │   └── main.py               # FastAPI application lifecycle and entrypoint
│   ├── requirements.txt          # Python backend dependencies
│   ├── .env.example
│   └── .gitignore
│
├── data-engine/                  # Data Science & Big Data Analytics Layer
│   ├── ingestion/                # Data connectors (public registries, owner uploads)
│   ├── cleaning/                 # Data deduplication, sanitization, and imputation
│   ├── features/                 # Financial ratios, operational velocity features
│   ├── analytics/                # Cohort aggregation, statistical distribution percentiles
│   └── scoring/                  # Mathematical, explainable Business Health Score formula
│
├── ml/                           # Machine Learning Layer
│   ├── models/                   # Serialized model registries (.joblib, .onnx)
│   ├── training/                 # Model training pipelines & hyperparameter tuning
│   └── evaluation/               # Cross-validation, metric tracking, explainability (SHAP)
│
├── ai/                           # Local AI & NLP Layer
│   └── ollama/                   # Local LLM service config, prompt templates, docker compose
│
├── database/                     # PostgreSQL storage & migrations
│   ├── schema/                   # PostgreSQL DDL schemas (businesses, metrics, scores)
│   │   └── 001_initial_schema.sql
│   └── migrations/               # Database versioned migration scripts
│
├── notebooks/                    # Jupyter notebooks for exploratory data analysis (EDA)
├── tests/                        # Automated testing suite
│   ├── backend/                  # API endpoint tests (FastAPI + AsyncClient + Pytest)
│   └── data_engine/              # Data science pipeline tests
│
├── .gitignore                    # Global git ignore configuration
├── .env.example                  # Consolidated environment variable template
└── README.md                     # Documentation & setup guide
```

---

## Getting Started Locally

### Prerequisites
- **Node.js**: v18.0.0 or higher (`node -v`)
- **npm**: v9.0.0 or higher (`npm -v`)
- **Python**: v3.10 or higher (`python --version`)
- **Git**: Installed and configured

---

### 1. Backend Setup (FastAPI)

1. Open a terminal and navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - **macOS / Linux**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Install backend dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Configure environment variables:
   ```bash
   cp .env.example .env
   ```

5. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

6. Verify the backend:
   - Open [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
   - Interactive Swagger API documentation: [http://localhost:8000/docs](http://localhost:8000/docs)
   - ReDoc documentation: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 2. Frontend Setup (Next.js)

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env.local
   ```
   *(Ensure `NEXT_PUBLIC_API_URL=http://localhost:8000` is present)*

4. Start the Next.js development server:
   ```bash
   npm run dev
   ```

5. Open [http://localhost:3000](http://localhost:3000) in your browser:
   - The landing page displays:
     - **Stanleaf**
     - **Business Intelligence, Simplified.**
     - Real-time live status indicator polling the FastAPI backend at `http://localhost:8000/api/v1/health`.

---

### 3. Running Automated Tests

Run the test suite using pytest from the workspace root or backend directory:

```powershell
# From the backend directory with active virtual environment:
pytest ../tests/backend -v
```

Expected output:
```
tests/backend/test_health.py::test_health_endpoint_v1 PASSED
tests/backend/test_health.py::test_health_endpoint_convenience PASSED
tests/backend/test_health.py::test_root_endpoint PASSED
```

---

## CORS Configuration

FastAPI is configured via `app/core/cors.py` to allow cross-origin requests from the Next.js frontend running at `http://localhost:3000` (and `http://127.0.0.1:3000`). Additional allowed origins can be specified in `backend/.env` using the `CORS_ORIGINS` comma-separated list.

---

## Architectural Principles & Ground Rules

1. **Explainability Over Black Boxes**: All business health scores must be mathematically explainable with weighted sub-indices. No opaque "AI score" without feature attribution.
2. **Data Science Decoupling**: Algorithms and feature transformations reside exclusively in `data-engine/` and `ml/`, never in web controllers or UI components.
3. **Reproducibility**: All exploratory work in `notebooks/` must transition to tested, modular functions in `data-engine/`.
4. **Data Privacy**: Local LLM workflows via Ollama are designed to prevent sensitive enterprise financials from being transmitted to third-party endpoints.
