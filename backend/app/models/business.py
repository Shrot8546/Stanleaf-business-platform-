import uuid
from sqlalchemy import Column, String, Integer, Float, DateTime, Uuid
from sqlalchemy.sql import func
from app.core.database import Base


class Business(Base):
    __tablename__ = "businesses"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False, index=True)
    industry = Column(String(255), nullable=False, index=True)
    location = Column(String(255), nullable=False)
    website = Column(String(500), nullable=True)
    business_age_years = Column(Integer, nullable=True)
    revenue_range = Column(String(100), nullable=True)
    employee_count = Column(Integer, nullable=True)
    customer_count = Column(Integer, nullable=True)
    marketing_spend_monthly = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Business(id={self.id}, name='{self.name}', industry='{self.industry}')>"
