"""
Stanleaf Data Engine
====================
Core Data Science & Big Data Analytics engine for Stanleaf.

Pipeline Stages:
1. Ingestion: Ingests raw public business data and owner-uploaded records.
2. Cleaning: Cleans, validates, sanitizes, and normalizes input data.
3. Features: Computes domain-specific financial and operational features.
4. Analytics: Reusable descriptive calculations and aggregation helpers.
5. Scoring: Interface reserved for Step 5 (Business Health Score Formula).
"""

from .pipeline import DataEngineeringPipeline, PipelineOutput, PIPELINE_VERSION
from .ingestion import DataExtractor, ExtractedBusinessData, BusinessNotFoundError
from .cleaning import DataCleaner, CleanedMetric, ValidationResult, MetricStatus
from .features import FeatureEngineer, DerivedFeature
from .scoring import BaseScoringEngine

__version__ = PIPELINE_VERSION

__all__ = [
    "DataEngineeringPipeline",
    "PipelineOutput",
    "PIPELINE_VERSION",
    "DataExtractor",
    "ExtractedBusinessData",
    "BusinessNotFoundError",
    "DataCleaner",
    "CleanedMetric",
    "ValidationResult",
    "MetricStatus",
    "FeatureEngineer",
    "DerivedFeature",
    "BaseScoringEngine",
]
