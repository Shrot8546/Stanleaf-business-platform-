import re
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, field_validator, ConfigDict

# Regular expression to validate standard web addresses (with or without http(s)://)
URL_REGEX = re.compile(
    r"^(https?:\/\/)?"  # optional scheme
    r"([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}"  # domain
    r"(:\d{1,5})?"  # optional port
    r"(\/[^\s]*)?$",  # optional path
    re.IGNORECASE,
)


class BusinessBase(BaseModel):
    name: str = Field(..., description="Business name", min_length=1, max_length=255)
    industry: str = Field(..., description="Industry sector", min_length=1, max_length=255)
    location: str = Field(..., description="Operating location or city/state/country", min_length=1, max_length=255)
    website: Optional[str] = Field(None, description="Official business website URL", max_length=500)
    business_age_years: Optional[int] = Field(None, ge=0, description="Age of business in years")
    revenue_range: Optional[str] = Field(None, description="Annual revenue bracket", max_length=100)
    employee_count: Optional[int] = Field(None, ge=0, description="Total headcount / employees")
    customer_count: Optional[int] = Field(None, ge=0, description="Active customer base count")
    marketing_spend_monthly: Optional[float] = Field(None, ge=0.0, description="Monthly marketing expenditure")

    @field_validator("name", "industry", "location")
    @classmethod
    def validate_non_empty_strings(cls, v: str, info) -> str:
        if not v or not v.strip():
            raise ValueError(f"{info.field_name} cannot be empty or blank whitespace.")
        return v.strip()

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        if not trimmed:
            return None
        if not URL_REGEX.match(trimmed):
            raise ValueError("Website must be a valid URL format (e.g. 'https://example.com' or 'example.com').")
        return trimmed

    @field_validator("revenue_range")
    @classmethod
    def clean_optional_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        trimmed = v.strip()
        return trimmed if trimmed else None


class BusinessCreate(BusinessBase):
    pass


class BusinessResponse(BusinessBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
