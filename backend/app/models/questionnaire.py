import uuid
from sqlalchemy import (
    Column,
    String,
    Float,
    Text,
    DateTime,
    Uuid,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class QuestionnaireResponse(Base):
    __tablename__ = "questionnaire_responses"

    id = Column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
        index=True,
    )
    business_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("businesses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    question_id = Column(String(100), nullable=False, index=True)
    industry = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False)
    value = Column(Text, nullable=False)
    numeric_value = Column(Float, nullable=True)
    data_type = Column(String(50), nullable=False)
    unit = Column(String(50), nullable=True)

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

    __table_args__ = (
        UniqueConstraint("business_id", "question_id", name="uq_business_question"),
    )

    def __repr__(self) -> str:
        return f"<QuestionnaireResponse(business_id={self.business_id}, question_id='{self.question_id}', value='{self.value}')>"
