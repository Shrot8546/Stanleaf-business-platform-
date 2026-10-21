"""
Stanleaf Data Engine — Ingestion Models
=======================================
Structured transfer models for data extracted from storage or input streams.
"""

from typing import Optional, List, Dict, Any, Union
from uuid import UUID
from datetime import datetime, timezone
from pydantic import BaseModel, Field


class RawQuestionnaireResponseItem(BaseModel):
    """
    Representation of an ingested questionnaire response record.
    """
    question_id: str
    industry: str
    category: str
    value: str
    numeric_value: Optional[float] = None
    data_type: str
    unit: Optional[str] = None
    period: str = "monthly"


class ExtractedBusinessData(BaseModel):
    """
    Structured data package extracted for a single business entity,
    combining core business registration profile and questionnaire metrics.
    """
    business_id: Union[str, UUID]
    name: str
    industry: str
    location: str
    website: Optional[str] = None
    business_age_years: Optional[int] = None
    revenue_range: Optional[str] = None
    employee_count: Optional[int] = None
    customer_count: Optional[int] = None
    marketing_spend_monthly: Optional[float] = None
    responses: List[RawQuestionnaireResponseItem] = Field(default_factory=list)
    extracted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "stanleaf_db"

    def get_response_by_id(self, question_id: str) -> Optional[RawQuestionnaireResponseItem]:
        """Finds a specific response item by canonical question ID."""
        for r in self.responses:
            if r.question_id == question_id:
                return r
        return None

    def get_response_dict(self) -> Dict[str, Any]:
        """Maps question IDs to their raw string values."""
        return {r.question_id: r.value for r in self.responses}

    def get_numeric_response_dict(self) -> Dict[str, Optional[float]]:
        """Maps question IDs to their parsed numeric values."""
        return {r.question_id: r.numeric_value for r in self.responses}
