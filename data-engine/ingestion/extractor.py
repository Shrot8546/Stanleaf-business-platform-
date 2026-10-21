"""
Stanleaf Data Engine — Ingestion Extractor
==========================================
Extracts persisted business profile and questionnaire responses from
the database repository or raw dictionary records.
"""

from typing import Union, Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timezone

from .models import ExtractedBusinessData, RawQuestionnaireResponseItem


class BusinessNotFoundError(Exception):
    """Raised when a requested business ID does not exist in the system."""
    def __init__(self, business_id: Union[str, UUID]):
        self.business_id = str(business_id)
        super().__init__(f"Business with ID '{self.business_id}' was not found.")


class DataExtractor:
    """
    Standard ingestion extractor interfacing between the database layer
    and the analytical data engineering pipeline.
    """

    @classmethod
    def extract_from_db(cls, db: Any, business_id: Union[str, UUID]) -> ExtractedBusinessData:
        """
        Retrieves business profile and questionnaire responses via SQLAlchemy session.
        Reuses existing BusinessRepository and QuestionnaireRepository without duplicating DB queries.
        """
        # Convert to UUID if string
        if isinstance(business_id, str):
            try:
                target_uuid = UUID(business_id)
            except ValueError:
                raise BusinessNotFoundError(business_id)
        else:
            target_uuid = business_id

        # Import repository lazily to keep data-engine modular and avoid circular imports
        try:
            from app.repositories.business import BusinessRepository
            from app.repositories.questionnaire import QuestionnaireRepository
        except ImportError:
            raise RuntimeError(
                "Backend repositories are not available in the current Python environment. "
                "Ensure Stanleaf backend is in sys.path or use DataExtractor.from_records()."
            )

        business = BusinessRepository.get_by_id(db, target_uuid)
        if not business:
            raise BusinessNotFoundError(target_uuid)

        db_responses = QuestionnaireRepository.get_by_business_id(db, target_uuid)

        response_items: List[RawQuestionnaireResponseItem] = []
        for r in db_responses:
            response_items.append(
                RawQuestionnaireResponseItem(
                    question_id=r.question_id,
                    industry=r.industry,
                    category=r.category,
                    value=r.value,
                    numeric_value=r.numeric_value,
                    data_type=r.data_type,
                    unit=r.unit,
                    period="monthly",
                )
            )

        return ExtractedBusinessData(
            business_id=str(business.id),
            name=business.name,
            industry=business.industry,
            location=business.location,
            website=business.website,
            business_age_years=business.business_age_years,
            revenue_range=business.revenue_range,
            employee_count=business.employee_count,
            customer_count=business.customer_count,
            marketing_spend_monthly=business.marketing_spend_monthly,
            responses=response_items,
            extracted_at=datetime.now(timezone.utc),
            source="stanleaf_db",
        )

    @classmethod
    def from_records(
        cls,
        business_profile: Dict[str, Any],
        questionnaire_responses: Optional[List[Dict[str, Any]]] = None,
        source: str = "memory_records",
    ) -> ExtractedBusinessData:
        """
        Instantiates an ExtractedBusinessData object directly from dictionaries.
        Enables offline batch pipelines, isolated unit tests, and external file ingestion.
        """
        b_id = str(business_profile.get("id") or business_profile.get("business_id", "00000000-0000-0000-0000-000000000000"))
        
        response_items: List[RawQuestionnaireResponseItem] = []
        if questionnaire_responses:
            for item in questionnaire_responses:
                # Calculate numeric value if not provided explicitly
                num_val = item.get("numeric_value")
                if num_val is None and "value" in item:
                    try:
                        num_val = float(item["value"])
                    except (ValueError, TypeError):
                        num_val = None

                response_items.append(
                    RawQuestionnaireResponseItem(
                        question_id=item["question_id"],
                        industry=item.get("industry", business_profile.get("industry", "general")),
                        category=item.get("category", "General"),
                        value=str(item.get("value", "")),
                        numeric_value=num_val,
                        data_type=item.get("data_type", "decimal"),
                        unit=item.get("unit"),
                        period=item.get("period", "monthly"),
                    )
                )

        return ExtractedBusinessData(
            business_id=b_id,
            name=business_profile.get("name", "Unnamed Business"),
            industry=business_profile.get("industry", "general"),
            location=business_profile.get("location", "Unknown"),
            website=business_profile.get("website"),
            business_age_years=business_profile.get("business_age_years"),
            revenue_range=business_profile.get("revenue_range"),
            employee_count=business_profile.get("employee_count"),
            customer_count=business_profile.get("customer_count"),
            marketing_spend_monthly=business_profile.get("marketing_spend_monthly"),
            responses=response_items,
            extracted_at=datetime.now(timezone.utc),
            source=source,
        )
