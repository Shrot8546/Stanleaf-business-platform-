from typing import List, Dict, Any, Optional
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.business import BusinessRepository
from app.repositories.questionnaire import QuestionnaireRepository
from app.schemas.questionnaire import (
    QuestionItem,
    QuestionnaireDefinition,
    QuestionnaireSubmission,
    QuestionnaireResponseOut,
    QuestionnaireSubmissionResult,
)
from app.services.questionnaire_definitions import (
    get_questionnaire_definition,
    normalize_industry,
    list_supported_industries,
)


class QuestionnaireService:
    """
    Business logic and validation service for industry-specific questionnaires.
    """

    @staticmethod
    def get_definition(industry: str) -> QuestionnaireDefinition:
        """
        Retrieves the structured questionnaire definition for a given industry.
        """
        definition_data = get_questionnaire_definition(industry)
        if not definition_data:
            supported = ", ".join(list_supported_industries())
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Questionnaire not found for industry '{industry}'. Currently supported industries: {supported}.",
            )

        questions = [QuestionItem(**q) for q in definition_data["questions"]]
        return QuestionnaireDefinition(
            industry=definition_data["industry"],
            title=definition_data["title"],
            description=definition_data["description"],
            total_questions=len(questions),
            questions=questions,
        )

    @staticmethod
    def submit_responses(
        db: Session,
        business_id: UUID,
        submission: QuestionnaireSubmission,
    ) -> QuestionnaireSubmissionResult:
        """
        Validates and persists submitted questionnaire responses for a business entity.
        """
        # 1. Verify business existence
        business = BusinessRepository.get_by_id(db=db, business_id=business_id)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business with ID '{business_id}' not found.",
            )

        # 2. Verify business industry has an active questionnaire
        normalized_industry = normalize_industry(business.industry)
        if not normalized_industry:
            supported = ", ".join(list_supported_industries())
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Business industry '{business.industry}' does not have a supported questionnaire. Supported industries: {supported}.",
            )

        definition = get_questionnaire_definition(normalized_industry)
        if not definition:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Questionnaire definition unavailable for '{normalized_industry}'.",
            )

        questions_map: Dict[str, Dict[str, Any]] = {
            q["id"]: q for q in definition["questions"]
        }

        # 3. Check for duplicate questions in submission
        seen_question_ids = set()
        for item in submission.responses:
            if item.question_id in seen_question_ids:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"Duplicate response submitted for question ID '{item.question_id}'.",
                )
            seen_question_ids.add(item.question_id)

        # 4. Check for invalid question IDs
        for item in submission.responses:
            if item.question_id not in questions_map:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail=f"Invalid question ID '{item.question_id}' for industry '{normalized_industry}'.",
                )

        # 5. Check all required questions are provided
        required_questions = [
            q["id"] for q in definition["questions"] if q["required"]
        ]
        missing_required = [
            qid for qid in required_questions if qid not in seen_question_ids
        ]
        if missing_required:
            missing_names = [questions_map[qid]["question_text"] for qid in missing_required]
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Missing required responses for: {', '.join(missing_names)} ({', '.join(missing_required)}).",
            )

        # 6. Validate values, types, and ranges
        response_dicts: List[Dict[str, Any]] = []

        for item in submission.responses:
            q_def = questions_map[item.question_id]
            data_type = q_def["data_type"]
            raw_val = item.value

            # Skip empty non-required values if None or blank
            if raw_val is None or (isinstance(raw_val, str) and not raw_val.strip()):
                if q_def["required"]:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail=f"Question '{q_def['question_text']}' ({item.question_id}) cannot be blank.",
                    )
                continue

            parsed_numeric: Optional[float] = None
            str_value = str(raw_val).strip()

            if data_type in ("integer", "decimal", "currency", "percentage"):
                try:
                    num_val = float(raw_val)
                except (ValueError, TypeError):
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail=f"Value for '{q_def['question_text']}' must be a valid number.",
                    )

                if data_type == "integer":
                    if not float(raw_val).is_integer():
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail=f"Value for '{q_def['question_text']}' must be an integer.",
                        )
                    parsed_numeric = float(int(num_val))
                    str_value = str(int(num_val))
                else:
                    parsed_numeric = num_val
                    str_value = str(num_val)

                # Min value constraint check
                if q_def.get("min_value") is not None and num_val < q_def["min_value"]:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail=f"Value for '{q_def['question_text']}' cannot be less than {q_def['min_value']}.",
                    )

                # Max value constraint check
                if q_def.get("max_value") is not None and num_val > q_def["max_value"]:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail=f"Value for '{q_def['question_text']}' cannot exceed {q_def['max_value']}.",
                    )

            elif data_type == "boolean":
                if isinstance(raw_val, bool):
                    bool_val = raw_val
                elif str_value.lower() in ("true", "1", "yes"):
                    bool_val = True
                elif str_value.lower() in ("false", "0", "no"):
                    bool_val = False
                else:
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail=f"Value for '{q_def['question_text']}' must be a boolean (true/false).",
                    )
                str_value = str(bool_val).lower()
                parsed_numeric = 1.0 if bool_val else 0.0

            elif data_type == "select":
                valid_options = q_def.get("options") or []
                if valid_options and str_value not in valid_options:
                    options_str = ", ".join(valid_options)
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                        detail=f"Value for '{q_def['question_text']}' must be one of: {options_str}.",
                    )

            response_dicts.append({
                "question_id": item.question_id,
                "industry": normalized_industry,
                "category": q_def["category"],
                "value": str_value,
                "numeric_value": parsed_numeric,
                "data_type": data_type,
                "unit": q_def.get("unit"),
            })

        # 7. Persist to database
        saved_records = QuestionnaireRepository.save_responses(
            db=db,
            business_id=business_id,
            response_dicts=response_dicts,
        )

        return QuestionnaireSubmissionResult(
            business_id=business_id,
            industry=normalized_industry,
            responses_count=len(saved_records),
            responses=[QuestionnaireResponseOut.model_validate(r) for r in saved_records],
        )

    @staticmethod
    def get_responses(db: Session, business_id: UUID) -> List[QuestionnaireResponseOut]:
        """
        Retrieves all stored questionnaire responses for a business entity.
        """
        business = BusinessRepository.get_by_id(db=db, business_id=business_id)
        if not business:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business with ID '{business_id}' not found.",
            )

        records = QuestionnaireRepository.get_by_business_id(db=db, business_id=business_id)
        return [QuestionnaireResponseOut.model_validate(r) for r in records]
