"""
Stanleaf Data Engine — Feature Models
=====================================
Models representing derived analytical features, metadata, and calculation rules.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class DerivedFeature(BaseModel):
    """
    Representation of an engineered analytical feature with full lineage and formula metadata.
    """
    name: str
    value: Optional[float] = None
    unit: str
    source_inputs: List[str] = Field(default_factory=list)
    derivation_rule: str
    status: str = "computed"  # "computed" | "skipped_missing_input" | "skipped_zero_division"
    notes: Optional[str] = None
