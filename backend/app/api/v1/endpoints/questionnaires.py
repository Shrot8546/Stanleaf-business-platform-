from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.questionnaire import (
    QuestionnaireDefinition,
    QuestionnaireSubmission,
    QuestionnaireResponseOut,
    QuestionnaireSubmissionResult,
)
from app.services.questionnaire import QuestionnaireService

router = APIRouter()


@router.get(
    "/questionnaires/{industry}",
    response_model=QuestionnaireDefinition,
    status_code=status.HTTP_200_OK,
    summary="Get industry questionnaire definition",
    description="Retrieves the structured diagnostic questionnaire for an industry with questions ordered by display_order.",
)
def get_industry_questionnaire(
    industry: str,
) -> QuestionnaireDefinition:
    return QuestionnaireService.get_definition(industry=industry)


@router.post(
    "/businesses/{business_id}/questionnaire",
    response_model=QuestionnaireSubmissionResult,
    status_code=status.HTTP_201_CREATED,
    summary="Submit business questionnaire responses",
    description="Validates and persists industry-specific questionnaire answers for a registered business entity.",
)
def submit_business_questionnaire(
    business_id: UUID,
    submission: QuestionnaireSubmission,
    db: Session = Depends(get_db),
) -> QuestionnaireSubmissionResult:
    return QuestionnaireService.submit_responses(
        db=db,
        business_id=business_id,
        submission=submission,
    )


@router.get(
    "/businesses/{business_id}/questionnaire",
    response_model=List[QuestionnaireResponseOut],
    status_code=status.HTTP_200_OK,
    summary="Get stored business questionnaire responses",
    description="Retrieves all persisted questionnaire response metrics for a registered business entity.",
)
def get_business_questionnaire(
    business_id: UUID,
    db: Session = Depends(get_db),
) -> List[QuestionnaireResponseOut]:
    return QuestionnaireService.get_responses(
        db=db,
        business_id=business_id,
    )
