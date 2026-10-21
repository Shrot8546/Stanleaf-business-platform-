"""
Stanleaf API — Data Processing Endpoint
=======================================
Triggers the Data Engineering pipeline on persisted business profile
and questionnaire response metrics.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.data_processing import DataProcessingResponse
from data_engine.ingestion import DataExtractor, BusinessNotFoundError
from data_engine.pipeline import DataEngineeringPipeline

router = APIRouter()


@router.post(
    "/businesses/{business_id}/data-processing",
    response_model=DataProcessingResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute data engineering pipeline for a business",
    description=(
        "Retrieves persisted business profile and questionnaire responses, executes data cleaning, "
        "unit and percentage normalization, and derives domain-specific analytical features. "
        "Returns the structured, validated feature set for future scoring."
    ),
)
def run_data_processing(
    business_id: UUID,
    db: Session = Depends(get_db),
) -> DataProcessingResponse:
    """
    Executes the deterministic data engineering pipeline for the specified business.
    Returns 404 if the business does not exist.
    """
    try:
        extracted_data = DataExtractor.extract_from_db(db=db, business_id=business_id)
    except BusinessNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID '{business_id}' was not found.",
        )

    pipeline = DataEngineeringPipeline()
    output = pipeline.run(extracted_data)
    return DataProcessingResponse(**output.to_dict())


@router.get(
    "/businesses/{business_id}/data-processing",
    response_model=DataProcessingResponse,
    status_code=status.HTTP_200_OK,
    summary="Get data processing results for a business (read-only)",
    description="Read-only query executing the deterministic pipeline on the current persisted data.",
)
def get_data_processing(
    business_id: UUID,
    db: Session = Depends(get_db),
) -> DataProcessingResponse:
    return run_data_processing(business_id=business_id, db=db)
