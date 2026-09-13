-- ==============================================================================
-- Stanleaf PostgreSQL Core Schema (Initial Architecture)
-- ==============================================================================

-- 1. Organizations & Entities
CREATE TABLE IF NOT EXISTS organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    registration_number VARCHAR(100) UNIQUE,
    industry_code VARCHAR(50), -- e.g., NAICS / SIC code
    country VARCHAR(3) DEFAULT 'USA',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. Financial Metrics Records
CREATE TABLE IF NOT EXISTS financial_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    revenue NUMERIC(15, 2),
    gross_profit NUMERIC(15, 2),
    net_income NUMERIC(15, 2),
    operating_expenses NUMERIC(15, 2),
    total_assets NUMERIC(15, 2),
    total_liabilities NUMERIC(15, 2),
    cash_flow_operating NUMERIC(15, 2),
    source_type VARCHAR(50) DEFAULT 'owner_provided', -- 'owner_provided', 'public_filing', 'registry'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. Operational & Market Indicators
CREATE TABLE IF NOT EXISTS operational_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    employee_count INT,
    customer_count INT,
    churn_rate NUMERIC(5, 4),
    burn_rate_monthly NUMERIC(15, 2),
    runway_months NUMERIC(6, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 4. Explainable Business Health Scores
CREATE TABLE IF NOT EXISTS health_scores (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    overall_score NUMERIC(5, 2) NOT NULL, -- Scale 0 - 100
    financial_subscore NUMERIC(5, 2),
    operational_subscore NUMERIC(5, 2),
    market_risk_subscore NUMERIC(5, 2),
    score_confidence NUMERIC(3, 2), -- Scale 0.0 - 1.0
    explanation_metadata JSONB,     -- Explainable factor decomposition and weights
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 5. Industry Benchmarks & Percentiles
CREATE TABLE IF NOT EXISTS industry_benchmarks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    industry_code VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    percentile_25 NUMERIC(15, 4),
    percentile_50 NUMERIC(15, 4), -- Median
    percentile_75 NUMERIC(15, 4),
    sample_size INT,
    effective_year INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(industry_code, metric_name, effective_year)
);

-- Indices for rapid querying
CREATE INDEX IF NOT EXISTS idx_org_industry ON organizations(industry_code);
CREATE INDEX IF NOT EXISTS idx_financial_org ON financial_metrics(organization_id);
CREATE INDEX IF NOT EXISTS idx_health_scores_org ON health_scores(organization_id, computed_at DESC);
