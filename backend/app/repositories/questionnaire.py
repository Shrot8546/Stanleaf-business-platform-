from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from app.models.questionnaire import QuestionnaireResponse


class QuestionnaireRepository:
    """
    Repository for persisting and retrieving questionnaire responses.
    """

    @staticmethod
    def save_responses(
        db: Session,
        business_id: UUID,
        response_dicts: List[Dict[str, Any]],
    ) -> List[QuestionnaireResponse]:
        """
        Atomically replaces existing questionnaire responses for the business
        with the newly submitted responses.
        """
        # Remove any existing responses for this business to ensure idempotency
        db.query(QuestionnaireResponse).filter(
            QuestionnaireResponse.business_id == business_id
        ).delete()

        # Build model instances
        new_responses = [
            QuestionnaireResponse(
                business_id=business_id,
                question_id=item["question_id"],
                industry=item["industry"],
                category=item["category"],
                value=item["value"],
                numeric_value=item["numeric_value"],
                data_type=item["data_type"],
                unit=item.get("unit"),
            )
            for item in response_dicts
        ]

        db.add_all(new_responses)
        db.commit()

        for resp in new_responses:
            db.refresh(resp)

        return new_responses

    @staticmethod
    def get_by_business_id(db: Session, business_id: UUID) -> List[QuestionnaireResponse]:
        """
        Retrieves all stored questionnaire responses for a business.
        """
        return (
            db.query(QuestionnaireResponse)
            .filter(QuestionnaireResponse.business_id == business_id)
            .order_by(QuestionnaireResponse.category, QuestionnaireResponse.question_id)
            .all()
        )

    @staticmethod
    def count_by_business_id(db: Session, business_id: UUID) -> int:
        """
        Returns count of responses for a business.
        """
        return (
            db.query(QuestionnaireResponse)
            .filter(QuestionnaireResponse.business_id == business_id)
            .count()
        )
