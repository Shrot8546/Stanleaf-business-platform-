# Stanleaf Data Engine (Data Science & Analytics Layer)

The **Data Engine** is the core analytical and big data processing layer of Stanleaf. Built as part of a Computer Science Engineering capstone specializing in Data Science and Big Data Analytics, it enforces clean separation of concerns across the analytical pipeline.

## Architectural Layers

```
data-engine/
├── ingestion/   # Stage 1: Data ingestion connectors & schema validation
├── cleaning/    # Stage 2: Data wrangling, imputation, outlier detection
├── features/    # Stage 3: Domain-specific feature engineering
├── analytics/   # Stage 4: Aggregation, cohort analysis, and distribution calculations
└── scoring/     # Stage 5: Explainable Business Health Score algorithms
```

### 1. Ingestion (`ingestion/`)
- Public financial filings, registry data, and web metrics.
- Owner-provided accounting records, CSV uploads, and ERP exports.
- Schema enforcement and raw event logging.

### 2. Cleaning (`cleaning/`)
- Deduplication and reconciliation across heterogeneous data sources.
- Handling missing data via statistical imputation.
- Currency normalization, unit standardization, and outlier flags.

### 3. Features (`features/`)
- Financial ratios (liquidity, solvency, profitability, operational efficiency).
- Growth trajectory and volatility indicators.
- Temporal aggregations and windowed rolling statistics.

### 4. Analytics (`analytics/`)
- Industry cohort grouping (by SIC/NAICS/industry code and revenue bands).
- Percentile ranking and benchmark distributions.
- Risk factor variance decomposition.

### 5. Scoring (`scoring/`)
- Transparent, explainable Business Health Score formula:
  $$\text{Health Score} = w_f \cdot S_{\text{financial}} + w_o \cdot S_{\text{operational}} + w_m \cdot S_{\text{market}}$$
- Factor attribution and contribution scoring for complete explainability.
- No black-box or unexplainable outputs.
