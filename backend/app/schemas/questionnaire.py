from datetime import datetime
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class QuestionItem(BaseModel):
    id: str = Field(..., description="Unique and stable question identifier (e.g. restaurant.monthly_revenue)")
    industry: str = Field(..., description="Industry sector key")
    category: str = Field(..., description="Functional business category (e.g. Financial, Customer, Operations)")
    question_text: str = Field(..., description="Human-readable question prompt")
    description: Optional[str] = Field(None, description="Detailed explanatory guidance for the metric")
    data_type: str = Field(..., description="Data type: currency, integer, decimal, percentage, text, boolean, select")
    unit: Optional[str] = Field(None, description="Display unit (e.g. ₹ / $, %, orders, stars, customers)")
    required: bool = Field(True, description="Whether an answer is mandatory for completing the diagnostic")
    min_value: Optional[float] = Field(None, description="Minimum acceptable numerical value")
    max_value: Optional[float] = Field(None, description="Maximum acceptable numerical value")
    options: Optional[List[str]] = Field(None, description="List of valid string options for select questions")
    display_order: int = Field(..., description="Display sequence order index")


class QuestionnaireDefinition(BaseModel):
    industry: str = Field(..., description="Normalized industry identifier")
    title: str = Field(..., description="Descriptive questionnaire title")
    description: str = Field(..., description="Overview of the questionnaire purpose")
    total_questions: int = Field(..., description="Total count of questions")
    questions: List[QuestionItem] = Field(..., description="Ordered list of questions")


class ResponseSubmissionItem(BaseModel):
    question_id: str = Field(..., description="Identifier of the answered question")
    value: Any = Field(..., description="Submitted response value (number, string, or boolean)")


class QuestionnaireSubmission(BaseModel):
    responses: List[ResponseSubmissionItem] = Field(..., description="List of question responses to record")


class QuestionnaireResponseOut(BaseModel):
    id: UUID
    business_id: UUID
    question_id: str
    industry: str
    category: str
    value: str
    numeric_value: Optional[float] = None
    data_type: str
    unit: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class QuestionnaireSubmissionResult(BaseModel):
    business_id: UUID
    industry: str
    responses_count: int
    responses: List[QuestionnaireResponseOut]
