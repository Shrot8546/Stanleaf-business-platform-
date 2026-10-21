export interface HealthResponse {
  status: string;
  service: string;
  version: string;
  environment: string;
  timestamp: string;
}

export interface Business {
  id: string;
  name: string;
  industry: string;
  location: string;
  website?: string | null;
  business_age_years?: number | null;
  revenue_range?: string | null;
  employee_count?: number | null;
  customer_count?: number | null;
  marketing_spend_monthly?: number | null;
  created_at: string;
  updated_at: string;
}

export interface BusinessCreateInput {
  name: string;
  industry: string;
  location: string;
  website?: string;
  business_age_years?: number;
  revenue_range?: string;
  employee_count?: number;
  customer_count?: number;
  marketing_spend_monthly?: number;
}

export interface QuestionItem {
  id: string;
  industry: string;
  category: string;
  question_text: string;
  description?: string | null;
  data_type: string;
  unit?: string | null;
  required: boolean;
  min_value?: number | null;
  max_value?: number | null;
  options?: string[] | null;
  display_order: number;
}

export interface QuestionnaireDefinition {
  industry: string;
  title: string;
  description: string;
  total_questions: number;
  questions: QuestionItem[];
}

export interface QuestionnaireResponseItem {
  id: string;
  business_id: string;
  question_id: string;
  industry: string;
  category: string;
  value: string;
  numeric_value?: number | null;
  data_type: string;
  unit?: string | null;
  created_at: string;
  updated_at: string;
}

export interface QuestionnaireSubmissionResult {
  business_id: string;
  industry: string;
  responses_count: number;
  responses: QuestionnaireResponseItem[];
}

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchHealthStatus(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/health`, {
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`API health check failed with status: ${response.status}`);
  }

  return response.json();
}

export async function createBusiness(
  input: BusinessCreateInput
): Promise<Business> {
  const response = await fetch(`${API_BASE_URL}/api/v1/businesses`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(input),
  });

  if (!response.ok) {
    let errorDetail = `Failed with status ${response.status}`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        if (Array.isArray(errorJson.detail)) {
          errorDetail = errorJson.detail
            .map((e: { msg: string; loc?: string[] }) => `${e.loc?.slice(-1)[0] || "field"}: ${e.msg}`)
            .join("; ");
        } else {
          errorDetail = errorJson.detail;
        }
      }
    } catch {
      // Use fallback errorDetail
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export async function fetchBusinesses(): Promise<Business[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/businesses`, {
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch businesses: ${response.status}`);
  }

  return response.json();
}

export async function fetchBusinessById(id: string): Promise<Business> {
  const response = await fetch(`${API_BASE_URL}/api/v1/businesses/${id}`, {
    cache: "no-store",
    headers: {
      "Content-Type": "application/json",
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch business ${id}: ${response.status}`);
  }

  return response.json();
}

export async function fetchQuestionnaire(
  industry: string
): Promise<QuestionnaireDefinition> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/questionnaires/${encodeURIComponent(industry)}`,
    {
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    let errorDetail = `Failed to fetch questionnaire (${response.status})`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail = errorJson.detail;
      }
    } catch {
      // Use fallback
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export async function submitQuestionnaire(
  businessId: string,
  responses: { question_id: string; value: any }[]
): Promise<QuestionnaireSubmissionResult> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/businesses/${businessId}/questionnaire`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ responses }),
    }
  );

  if (!response.ok) {
    let errorDetail = `Failed to submit questionnaire (${response.status})`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        if (Array.isArray(errorJson.detail)) {
          errorDetail = errorJson.detail
            .map((e: { msg: string; loc?: string[] }) => `${e.loc?.slice(-1)[0] || "field"}: ${e.msg}`)
            .join("; ");
        } else {
          errorDetail = errorJson.detail;
        }
      }
    } catch {
      // Use fallback
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export async function fetchBusinessQuestionnaire(
  businessId: string
): Promise<QuestionnaireResponseItem[]> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/businesses/${businessId}/questionnaire`,
    {
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch questionnaire responses: ${response.status}`);
  }

  return response.json();
}

export interface CleanedMetricItem {
  metric_id: string;
  raw_value: any;
  value: number | string | null;
  data_type: string;
  unit?: string | null;
  period?: string | null;
  status: "valid" | "missing" | "invalid" | "derived";
  source_input: string;
  validation_notes: string[];
}

export interface DerivedFeatureItem {
  name: string;
  value: number | null;
  unit: string;
  source_inputs: string[];
  derivation_rule: string;
  status: "computed" | "skipped_missing_input" | "skipped_zero_division";
  notes?: string | null;
}

export interface DataProcessingOutput {
  business_id: string;
  industry: string;
  source_metrics: Record<string, any>;
  cleaned_metrics: Record<string, CleanedMetricItem>;
  derived_features: Record<string, DerivedFeatureItem>;
  missing_fields: string[];
  validation_errors: string[];
  data_quality_warnings: string[];
  processing_timestamp: string;
  pipeline_version: string;
}

export async function runDataProcessing(
  businessId: string
): Promise<DataProcessingOutput> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/businesses/${businessId}/data-processing`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    let errorDetail = `Data processing failed (${response.status})`;
    try {
      const errorJson = await response.json();
      if (errorJson.detail) {
        errorDetail = errorJson.detail;
      }
    } catch {
      // Use fallback
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export async function fetchDataProcessing(
  businessId: string
): Promise<DataProcessingOutput> {
  const response = await fetch(
    `${API_BASE_URL}/api/v1/businesses/${businessId}/data-processing`,
    {
      cache: "no-store",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  if (!response.ok) {
    throw new Error(`Failed to fetch data processing output: ${response.status}`);
  }

  return response.json();
}

