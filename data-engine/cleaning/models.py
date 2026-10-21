"""
Stanleaf Data Engine — Cleaning & Validation Models
===================================================
Models representing cleaned metrics, validation issues, and quality reports.
"""

from enum import Enum
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field


class MetricStatus(str, Enum):
    VALID = "valid"
    MISSING = "missing"
    INVALID = "invalid"
    DERIVED = "derived"


class CleanedMetric(BaseModel):
    """
    Standardized, validated metric representation with full provenance.
    """
    metric_id: str
    raw_value: Any = None
    value: Optional[Union[float, int, str]] = None
    data_type: str
    unit: Optional[str] = None
    period: Optional[str] = "monthly"
    status: MetricStatus = MetricStatus.VALID
    source_input: str
    validation_notes: List[str] = Field(default_factory=list)

    def is_numeric(self) -> bool:
        return isinstance(self.value, (int, float)) and not isinstance(self.value, bool)


class ValidationIssue(BaseModel):
    """
    Descriptive issue (error or warning) discovered during validation.
    """
    field: str
    issue_type: str
    message: str
    severity: str  # "error" | "warning"


class ValidationResult(BaseModel):
    """
    Structured outcome of the data validation and cleaning stage.
    """
    is_valid: bool
    errors: List[ValidationIssue] = Field(default_factory=list)
    warnings: List[ValidationIssue] = Field(default_factory=list)
    missing_required_fields: List[str] = Field(default_factory=list)
    missing_optional_fields: List[str] = Field(default_factory=list)
    invalid_fields: List[str] = Field(default_factory=list)
    cleaned_metrics: Dict[str, CleanedMetric] = Field(default_factory=dict)
    source_metrics: Dict[str, Any] = Field(default_factory=dict)

    def error_messages(self) -> List[str]:
        return [f"{e.field}: {e.message}" for e in self.errors]

    def warning_messages(self) -> List[str]:
        return [f"{w.field}: {w.message}" for w in self.warnings]
