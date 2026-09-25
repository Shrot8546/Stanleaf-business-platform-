from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.business import Business
from app.schemas.business import BusinessCreate


class BusinessRepository:
    """
    Data access repository for Business domain entity.
    Encapsulates all database interactions away from API route handlers.
    """

    @staticmethod
    def create(db: Session, business_in: BusinessCreate) -> Business:
        business = Business(
            name=business_in.name,
            industry=business_in.industry,
            location=business_in.location,
            website=business_in.website,
            business_age_years=business_in.business_age_years,
            revenue_range=business_in.revenue_range,
            employee_count=business_in.employee_count,
            customer_count=business_in.customer_count,
            marketing_spend_monthly=business_in.marketing_spend_monthly,
        )
        db.add(business)
        db.commit()
        db.refresh(business)
        return business

    @staticmethod
    def get_by_id(db: Session, business_id: UUID) -> Optional[Business]:
        return db.query(Business).filter(Business.id == business_id).first()

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Business]:
        return (
            db.query(Business)
            .order_by(Business.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    @staticmethod
    def count(db: Session) -> int:
        return db.query(Business).count()
