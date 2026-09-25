from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.business import BusinessRepository
from app.schemas.business import BusinessCreate, BusinessResponse

router = APIRouter()


@router.post(
    "",
    response_model=BusinessResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new business",
    description="Creates and persists a new business entity in the database.",
)
def create_business(
    business_in: BusinessCreate,
    db: Session = Depends(get_db),
) -> BusinessResponse:
    business = BusinessRepository.create(db=db, business_in=business_in)
    return BusinessResponse.model_validate(business)


@router.get(
    "/{business_id}",
    response_model=BusinessResponse,
    status_code=status.HTTP_200_OK,
    summary="Get business by ID",
    description="Retrieves a single business record by its unique UUID.",
)
def get_business(
    business_id: UUID,
    db: Session = Depends(get_db),
) -> BusinessResponse:
    business = BusinessRepository.get_by_id(db=db, business_id=business_id)
    if not business:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Business with ID '{business_id}' not found.",
        )
    return BusinessResponse.model_validate(business)


@router.get(
    "",
    response_model=List[BusinessResponse],
    status_code=status.HTTP_200_OK,
    summary="List all businesses",
    description="Retrieves a paginated list of all registered business entities.",
)
def list_businesses(
    skip: int = Query(0, ge=0, description="Records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum records to return"),
    db: Session = Depends(get_db),
) -> List[BusinessResponse]:
    businesses = BusinessRepository.get_all(db=db, skip=skip, limit=limit)
    return [BusinessResponse.model_validate(b) for b in businesses]
