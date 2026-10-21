"""
Stanleaf Data Engine — Pipeline Orchestrator & Output Schema
============================================================
Coordinates ingestion, cleaning, validation, normalization, and feature derivation
into a single deterministic pipeline execution producing structured output.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from ingestion.models import ExtractedBusinessData
from cleaning.models import CleanedMetric, ValidationResult
from cleaning.validator import DataCleaner
from features.models import DerivedFeature
from features.engineer import FeatureEngineer

PIPELINE_VERSION = "0.1.0"


class PipelineOutput(BaseModel):
    """
    Standardized, documented output schema of the Data Engineering pipeline.
    Fully JSON-serializable for API boundaries and future scoring consumption.
    """
    business_id: str
    industry: str
    source_metrics: Dict[str, Any]
    cleaned_metrics: Dict[str, Dict[str, Any]]
    derived_features: Dict[str, Dict[str, Any]]
    missing_fields: List[str]
    validation_errors: List[str]
    data_quality_warnings: List[str]
    processing_timestamp: str
    pipeline_version: str = PIPELINE_VERSION

    def to_dict(self) -> Dict[str, Any]:
        """Returns JSON-serializable primitive dictionary."""
        return self.model_dump()


class DataEngineeringPipeline:
    """
    Deterministic data engineering pipeline for Stanleaf.
    Transforms raw extracted business records into validated analytical features.
    """

    def __init__(self, version: str = PIPELINE_VERSION):
        self.version = version

    def run(self, extracted_data: ExtractedBusinessData) -> PipelineOutput:
        """
        Executes pipeline stages sequentially:
        1. Ingestion payload verification
        2. Validation, bounds checking, unit normalization, and outlier detection
        3. Domain-specific feature engineering
        4. Structured serialization
        """
        # Stage 2: Validation & Cleaning
        validation_result: ValidationResult = DataCleaner.clean_and_validate(extracted_data)

        # Stage 3: Feature Engineering
        features: Dict[str, DerivedFeature] = FeatureEngineer.engineer_features(
            cleaned_metrics=validation_result.cleaned_metrics,
            industry=extracted_data.industry,
        )

        # Serialize cleaned metrics for API compatibility
        serialized_cleaned: Dict[str, Dict[str, Any]] = {}
        for k, metric in validation_result.cleaned_metrics.items():
            serialized_cleaned[k] = {
                "metric_id": metric.metric_id,
                "raw_value": metric.raw_value,
                "value": metric.value,
                "data_type": metric.data_type,
                "unit": metric.unit,
                "period": metric.period,
                "status": metric.status.value,
                "source_input": metric.source_input,
                "validation_notes": metric.validation_notes,
            }

        # Serialize derived features for API compatibility
        serialized_features: Dict[str, Dict[str, Any]] = {}
        for k, feat in features.items():
            serialized_features[k] = {
                "name": feat.name,
                "value": feat.value,
                "unit": feat.unit,
                "source_inputs": feat.source_inputs,
                "derivation_rule": feat.derivation_rule,
                "status": feat.status,
                "notes": feat.notes,
            }

        # Combine missing fields
        missing_fields = list(
            dict.fromkeys(
                validation_result.missing_required_fields
                + validation_result.missing_optional_fields
            )
        )

        # Construct final output
        timestamp_str = datetime.now(timezone.utc).isoformat()

        return PipelineOutput(
            business_id=str(extracted_data.business_id),
            industry=extracted_data.industry,
            source_metrics=validation_result.source_metrics,
            cleaned_metrics=serialized_cleaned,
            derived_features=serialized_features,
            missing_fields=missing_fields,
            validation_errors=validation_result.error_messages(),
            data_quality_warnings=validation_result.warning_messages(),
            processing_timestamp=timestamp_str,
            pipeline_version=self.version,
        )
