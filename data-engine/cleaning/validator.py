"""
Stanleaf Data Engine — Data Cleaning and Validation
===================================================
Validates expected types, ranges, percentage bounds, units, reporting periods,
and industry compatibility. Normalizes representations without losing precision.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
import math

from ingestion.models import ExtractedBusinessData, RawQuestionnaireResponseItem
from analytics.calculations import is_within_bounds, check_period_compatibility
from .models import CleanedMetric, MetricStatus, ValidationIssue, ValidationResult

# Canonical definitions for fallback validation if backend is decoupled
CANONICAL_QUESTION_SPECS: Dict[str, Dict[str, Dict[str, Any]]] = {
    "restaurant": {
        "restaurant.monthly_revenue": {
            "canonical_id": "monthly_revenue",
            "category": "Financial",
            "data_type": "currency",
            "unit": "₹ / $",
            "required": True,
            "min_value": 0.0,
            "max_value": None,
            "period": "monthly",
        },
        "restaurant.monthly_expenses": {
            "canonical_id": "monthly_expenses",
            "category": "Financial",
            "data_type": "currency",
            "unit": "₹ / $",
            "required": True,
            "min_value": 0.0,
            "max_value": None,
            "period": "monthly",
        },
        "restaurant.average_order_value": {
            "canonical_id": "reported_average_order_value",
            "category": "Financial",
            "data_type": "currency",
            "unit": "₹ / $",
            "required": True,
            "min_value": 0.0,
            "max_value": None,
            "period": "monthly",
        },
        "restaurant.food_cost_percentage": {
            "canonical_id": "food_cost_percentage",
            "category": "Financial",
            "data_type": "percentage",
            "unit": "%",
            "required": False,
            "min_value": 0.0,
            "max_value": 100.0,
            "period": "monthly",
        },
        "restaurant.monthly_customers": {
            "canonical_id": "monthly_customers",
            "category": "Customer",
            "data_type": "integer",
            "unit": "customers",
            "required": True,
            "min_value": 0,
            "max_value": None,
            "period": "monthly",
        },
        "restaurant.repeat_customer_percentage": {
            "canonical_id": "repeat_customer_percentage",
            "category": "Customer",
            "data_type": "percentage",
            "unit": "%",
            "required": True,
            "min_value": 0.0,
            "max_value": 100.0,
            "period": "monthly",
        },
        "restaurant.employee_count": {
            "canonical_id": "employee_count",
            "category": "Operations",
            "data_type": "integer",
            "unit": "employees",
            "required": True,
            "min_value": 0,
            "max_value": None,
            "period": "instantaneous",
        },
        "restaurant.monthly_orders": {
            "canonical_id": "monthly_orders",
            "category": "Operations",
            "data_type": "integer",
            "unit": "orders",
            "required": True,
            "min_value": 0,
            "max_value": None,
            "period": "monthly",
        },
        "restaurant.table_count": {
            "canonical_id": "table_count",
            "category": "Operations",
            "data_type": "integer",
            "unit": "tables",
            "required": False,
            "min_value": 0,
            "max_value": None,
            "period": "instantaneous",
        },
        "restaurant.monthly_marketing_spend": {
            "canonical_id": "monthly_marketing_spend",
            "category": "Marketing",
            "data_type": "currency",
            "unit": "₹ / $",
            "required": False,
            "min_value": 0.0,
            "max_value": None,
            "period": "monthly",
        },
        "restaurant.average_rating": {
            "canonical_id": "average_rating",
            "category": "Reputation",
            "data_type": "decimal",
            "unit": "stars",
            "required": True,
            "min_value": 0.0,
            "max_value": 5.0,
            "period": "cumulative",
        },
        "restaurant.total_reviews": {
            "canonical_id": "total_reviews",
            "category": "Reputation",
            "data_type": "integer",
            "unit": "reviews",
            "required": False,
            "min_value": 0,
            "max_value": None,
            "period": "cumulative",
        },
    },
    "ecommerce": {
        "ecommerce.monthly_revenue": {
            "canonical_id": "monthly_revenue",
            "category": "Financial",
            "data_type": "currency",
            "unit": "₹ / $",
            "required": True,
            "min_value": 0.0,
            "max_value": None,
            "period": "monthly",
        },
        "ecommerce.monthly_expenses": {
            "canonical_id": "monthly_expenses",
            "category": "Financial",
            "data_type": "currency",
            "unit": "₹ / $",
            "required": True,
            "min_value": 0.0,
            "max_value": None,
            "period": "monthly",
        },
        "ecommerce.gross_margin_percentage": {
            "canonical_id": "gross_margin_percentage",
            "category": "Financial",
            "data_type": "percentage",
            "unit": "%",
            "required": True,
            "min_value": 0.0,
            "max_value": 100.0,
            "period": "monthly",
        },
        "ecommerce.monthly_orders": {
            "canonical_id": "monthly_orders",
            "category": "Customer",
            "data_type": "integer",
            "unit": "orders",
            "required": True,
            "min_value": 0,
            "max_value": None,
            "period": "monthly",
        },
        "ecommerce.repeat_purchase_percentage": {
            "canonical_id": "repeat_purchase_percentage",
            "category": "Customer",
            "data_type": "percentage",
            "unit": "%",
            "required": True,
            "min_value": 0.0,
            "max_value": 100.0,
            "period": "monthly",
        },
        "ecommerce.average_order_value": {
            "canonical_id": "reported_average_order_value",
            "category": "Operations",
            "data_type": "currency",
            "unit": "₹ / $",
            "required": True,
            "min_value": 0.0,
            "max_value": None,
            "period": "monthly",
        },
        "ecommerce.return_rate_percentage": {
            "canonical_id": "return_rate_percentage",
            "category": "Operations",
            "data_type": "percentage",
            "unit": "%",
            "required": True,
            "min_value": 0.0,
            "max_value": 100.0,
            "period": "monthly",
        },
        "ecommerce.monthly_marketing_spend": {
            "canonical_id": "monthly_marketing_spend",
            "category": "Marketing",
            "data_type": "currency",
            "unit": "₹ / $",
            "required": True,
            "min_value": 0.0,
            "max_value": None,
            "period": "monthly",
        },
        "ecommerce.customer_acquisition_cost": {
            "canonical_id": "customer_acquisition_cost",
            "category": "Marketing",
            "data_type": "currency",
            "unit": "₹ / $",
            "required": False,
            "min_value": 0.0,
            "max_value": None,
            "period": "monthly",
        },
        "ecommerce.monthly_website_traffic": {
            "canonical_id": "monthly_website_traffic",
            "category": "Growth",
            "data_type": "integer",
            "unit": "visitors",
            "required": True,
            "min_value": 0,
            "max_value": None,
            "period": "monthly",
        },
        "ecommerce.conversion_rate": {
            "canonical_id": "conversion_rate",
            "category": "Growth",
            "data_type": "percentage",
            "unit": "%",
            "required": True,
            "min_value": 0.0,
            "max_value": 100.0,
            "period": "monthly",
        },
    },
}


def normalize_industry_key(industry: str) -> str:
    """Normalizes industry string to canonical key ('restaurant' or 'ecommerce')."""
    norm = industry.strip().lower().replace("-", "").replace("_", "").replace(" ", "")
    if "restaurant" in norm or "food" in norm or "cafe" in norm:
        return "restaurant"
    if "ecommerce" in norm or "d2c" in norm or "retail" in norm or "store" in norm:
        return "ecommerce"
    return norm


class DataCleaner:
    """
    Validates and cleans extracted business metrics against domain specifications.
    Enforces type safety, range limits, percentage bounds, period compatibility,
    and prevents silent replacement of missing values.
    """

    @classmethod
    def clean_and_validate(cls, data: ExtractedBusinessData) -> ValidationResult:
        industry_key = normalize_industry_key(data.industry)
        specs = CANONICAL_QUESTION_SPECS.get(industry_key, {})

        errors: List[ValidationIssue] = []
        warnings: List[ValidationIssue] = []
        missing_required: List[str] = []
        missing_optional: List[str] = []
        invalid_fields: List[str] = []
        cleaned_metrics: Dict[str, CleanedMetric] = {}
        source_metrics: Dict[str, Any] = {}

        # 1. Record profile metrics
        source_metrics["business_id"] = str(data.business_id)
        source_metrics["industry"] = data.industry
        source_metrics["name"] = data.name

        if data.employee_count is not None:
            source_metrics["profile_employee_count"] = data.employee_count
            if data.employee_count < 0:
                errors.append(
                    ValidationIssue(
                        field="employee_count",
                        issue_type="range_error",
                        message="Profile employee count cannot be negative.",
                        severity="error",
                    )
                )
                invalid_fields.append("employee_count")

        if data.marketing_spend_monthly is not None:
            source_metrics["profile_marketing_spend"] = data.marketing_spend_monthly
            if data.marketing_spend_monthly < 0:
                errors.append(
                    ValidationIssue(
                        field="marketing_spend_monthly",
                        issue_type="range_error",
                        message="Profile marketing spend cannot be negative.",
                        severity="error",
                    )
                )
                invalid_fields.append("marketing_spend_monthly")

        # 2. Check for duplicate or conflicting question identifiers
        seen_questions: Set[str] = set()
        duplicate_questions: Set[str] = set()
        for r in data.responses:
            if r.question_id in seen_questions:
                duplicate_questions.add(r.question_id)
            seen_questions.add(r.question_id)

        for dup in duplicate_questions:
            errors.append(
                ValidationIssue(
                    field=dup,
                    issue_type="duplicate_identifier",
                    message=f"Duplicate response found for metric '{dup}'. Conflicting identifiers must be resolved.",
                    severity="error",
                )
            )
            invalid_fields.append(dup)

        # 3. Process each response
        responses_by_id = {r.question_id: r for r in data.responses}

        for q_id, spec in specs.items():
            canonical_name = spec["canonical_id"]
            resp = responses_by_id.get(q_id)

            if resp is None or resp.value is None or resp.value == "":
                # Value is missing
                if spec["required"]:
                    missing_required.append(q_id)
                    errors.append(
                        ValidationIssue(
                            field=q_id,
                            issue_type="missing_required",
                            message=f"Required metric '{q_id}' is missing.",
                            severity="error",
                        )
                    )
                else:
                    missing_optional.append(q_id)
                    warnings.append(
                        ValidationIssue(
                            field=q_id,
                            issue_type="missing_optional",
                            message=f"Optional metric '{q_id}' was not provided.",
                            severity="warning",
                        )
                    )

                # DO NOT replace missing with zero! Record as MISSING with None value
                cleaned_metrics[canonical_name] = CleanedMetric(
                    metric_id=canonical_name,
                    raw_value=None,
                    value=None,
                    data_type=spec["data_type"],
                    unit=spec["unit"],
                    period=spec["period"],
                    status=MetricStatus.MISSING,
                    source_input=f"questionnaire:{q_id}",
                    validation_notes=["Metric missing from source responses"],
                )
                source_metrics[q_id] = None
                continue

            # Record raw value in source metrics
            source_metrics[q_id] = resp.value

            # 4. Check Industry Compatibility
            resp_industry_key = normalize_industry_key(resp.industry)
            if resp_industry_key != industry_key:
                errors.append(
                    ValidationIssue(
                        field=q_id,
                        issue_type="incompatible_industry",
                        message=(
                            f"Metric '{q_id}' belongs to industry '{resp.industry}' "
                            f"which is incompatible with business industry '{data.industry}'."
                        ),
                        severity="error",
                    )
                )
                invalid_fields.append(q_id)

            # 5. Check Reporting Period Compatibility
            period_compat, period_err = check_period_compatibility(resp.period, spec["period"])
            if not period_compat:
                errors.append(
                    ValidationIssue(
                        field=q_id,
                        issue_type="incompatible_period",
                        message=period_err or f"Incompatible reporting period for '{q_id}'.",
                        severity="error",
                    )
                )
                invalid_fields.append(q_id)

            # 6. Parse and Validate Value Type
            parsed_val: Optional[Union[float, int, str]] = None
            is_valid_type = True
            val_str = str(resp.value).strip()

            if spec["data_type"] in ("currency", "decimal", "percentage"):
                # Clean currency/percentage formatting like "$", "₹", "%", commas
                cleaned_str = val_str.replace("$", "").replace("₹", "").replace("%", "").replace(",", "").strip()
                try:
                    parsed_val = float(cleaned_str)
                    if math.isnan(parsed_val) or math.isinf(parsed_val):
                        is_valid_type = False
                except ValueError:
                    is_valid_type = False

            elif spec["data_type"] == "integer":
                cleaned_str = val_str.replace(",", "").strip()
                try:
                    float_val = float(cleaned_str)
                    if not float_val.is_integer() or math.isnan(float_val) or math.isinf(float_val):
                        is_valid_type = False
                    else:
                        parsed_val = int(float_val)
                except ValueError:
                    is_valid_type = False
            else:
                parsed_val = val_str

            if not is_valid_type:
                errors.append(
                    ValidationIssue(
                        field=q_id,
                        issue_type="type_error",
                        message=f"Value '{resp.value}' could not be converted to expected type '{spec['data_type']}'.",
                        severity="error",
                    )
                )
                invalid_fields.append(q_id)
                cleaned_metrics[canonical_name] = CleanedMetric(
                    metric_id=canonical_name,
                    raw_value=resp.value,
                    value=None,
                    data_type=spec["data_type"],
                    unit=spec["unit"],
                    period=resp.period or spec["period"],
                    status=MetricStatus.INVALID,
                    source_input=f"questionnaire:{q_id}",
                    validation_notes=[f"Type conversion failure: cannot parse '{resp.value}' as {spec['data_type']}"],
                )
                continue

            # 7. Check Range & Bounds
            bounds_valid = is_within_bounds(
                parsed_val,
                min_value=spec["min_value"],
                max_value=spec["max_value"],
            )

            if not bounds_valid:
                # Specific percentage bound error message
                if spec["data_type"] == "percentage":
                    msg = f"Percentage value '{parsed_val}' is outside valid bounds [0.0%, 100.0%]."
                    issue_t = "percentage_bound"
                else:
                    msg = f"Value '{parsed_val}' is outside valid range [{spec['min_value']}, {spec['max_value']}]."
                    issue_t = "range_error"

                errors.append(
                    ValidationIssue(
                        field=q_id,
                        issue_type=issue_t,
                        message=msg,
                        severity="error",
                    )
                )
                invalid_fields.append(q_id)
                cleaned_metrics[canonical_name] = CleanedMetric(
                    metric_id=canonical_name,
                    raw_value=resp.value,
                    value=parsed_val,
                    data_type=spec["data_type"],
                    unit=spec["unit"],
                    period=resp.period or spec["period"],
                    status=MetricStatus.INVALID,
                    source_input=f"questionnaire:{q_id}",
                    validation_notes=[msg],
                )
                continue

            # 8. Check for Plausible Outliers (without automatically removing them)
            notes: List[str] = []
            if spec["data_type"] == "currency" and parsed_val is not None and parsed_val > 1e10:
                warnings.append(
                    ValidationIssue(
                        field=q_id,
                        issue_type="data_quality_warning",
                        message=f"Value '{parsed_val}' for '{q_id}' is exceptionally large. Flagged for review.",
                        severity="warning",
                    )
                )
                notes.append("High-magnitude outlier detected; preserved without truncation.")

            # Valid metric recorded
            cleaned_metrics[canonical_name] = CleanedMetric(
                metric_id=canonical_name,
                raw_value=resp.value,
                value=parsed_val,
                data_type=spec["data_type"],
                unit=spec["unit"],
                period=resp.period or spec["period"],
                status=MetricStatus.VALID,
                source_input=f"questionnaire:{q_id}",
                validation_notes=notes,
            )

        # 9. Check for Unrecognized or Cross-Industry Questions Submitted
        for r in data.responses:
            if r.question_id not in specs:
                # Question is not part of this industry's specs
                errors.append(
                    ValidationIssue(
                        field=r.question_id,
                        issue_type="incompatible_industry",
                        message=f"Question '{r.question_id}' is not recognized for industry '{data.industry}'.",
                        severity="error",
                    )
                )
                invalid_fields.append(r.question_id)

        # 10. Check Inter-Metric Consistency (Domain Warnings)
        # E.g. If expenses > revenue * 5
        rev_m = cleaned_metrics.get("monthly_revenue")
        exp_m = cleaned_metrics.get("monthly_expenses")
        if (
            rev_m
            and exp_m
            and rev_m.status == MetricStatus.VALID
            and exp_m.status == MetricStatus.VALID
            and rev_m.value is not None
            and exp_m.value is not None
        ):
            if float(exp_m.value) > float(rev_m.value) * 5.0 and float(rev_m.value) > 0:
                warnings.append(
                    ValidationIssue(
                        field="monthly_expenses",
                        issue_type="data_quality_warning",
                        message=(
                            f"Monthly expenses ({exp_m.value}) exceed 500% of monthly revenue ({rev_m.value}). "
                            "Unusual burn rate flagged for data quality review."
                        ),
                        severity="warning",
                    )
                )

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            missing_required_fields=missing_required,
            missing_optional_fields=missing_optional,
            invalid_fields=invalid_fields,
            cleaned_metrics=cleaned_metrics,
            source_metrics=source_metrics,
        )
