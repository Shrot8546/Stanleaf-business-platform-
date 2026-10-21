"""
Stanleaf Data Engine — Pipeline & Cleaning Unit Tests
=====================================================
Automated tests verifying:
- Valid restaurant input
- Valid e-commerce input
- Missing optional metrics (no silent zero replacement)
- Invalid numeric values
- Percentage bounds
- Division by zero safety
- Derived feature calculation precision
- Incompatible reporting periods
- Duplicate question IDs
- JSON serialization
- Deterministic repeated pipeline execution
- Scoring interface reservation
"""

import json
import pytest
from datetime import datetime, timezone

from data_engine.ingestion import DataExtractor, ExtractedBusinessData, RawQuestionnaireResponseItem
from data_engine.cleaning import DataCleaner, MetricStatus
from data_engine.features import FeatureEngineer
from data_engine.pipeline import DataEngineeringPipeline, PipelineOutput
from data_engine.scoring import BaseScoringEngine
from data_engine.analytics import safe_divide, calculate_percentage, check_period_compatibility


@pytest.fixture
def valid_restaurant_records():
    profile = {
        "id": "11111111-1111-1111-1111-111111111111",
        "name": "Bistro Bella",
        "industry": "Restaurant",
        "location": "Chicago, IL",
        "employee_count": 12,
        "marketing_spend_monthly": 20000.0,
    }
    responses = [
        {"question_id": "restaurant.monthly_revenue", "value": "500000", "numeric_value": 500000.0, "data_type": "currency", "unit": "₹ / $"},
        {"question_id": "restaurant.monthly_expenses", "value": "350000", "numeric_value": 350000.0, "data_type": "currency", "unit": "₹ / $"},
        {"question_id": "restaurant.average_order_value", "value": "500", "numeric_value": 500.0, "data_type": "currency", "unit": "₹ / $"},
        {"question_id": "restaurant.food_cost_percentage", "value": "32.5", "numeric_value": 32.5, "data_type": "percentage", "unit": "%"},
        {"question_id": "restaurant.monthly_customers", "value": "1200", "numeric_value": 1200.0, "data_type": "integer", "unit": "customers"},
        {"question_id": "restaurant.repeat_customer_percentage", "value": "45.0", "numeric_value": 45.0, "data_type": "percentage", "unit": "%"},
        {"question_id": "restaurant.employee_count", "value": "12", "numeric_value": 12.0, "data_type": "integer", "unit": "employees"},
        {"question_id": "restaurant.monthly_orders", "value": "1000", "numeric_value": 1000.0, "data_type": "integer", "unit": "orders"},
        {"question_id": "restaurant.table_count", "value": "25", "numeric_value": 25.0, "data_type": "integer", "unit": "tables"},
        {"question_id": "restaurant.monthly_marketing_spend", "value": "20000", "numeric_value": 20000.0, "data_type": "currency", "unit": "₹ / $"},
        {"question_id": "restaurant.average_rating", "value": "4.6", "numeric_value": 4.6, "data_type": "decimal", "unit": "stars"},
        {"question_id": "restaurant.total_reviews", "value": "340", "numeric_value": 340.0, "data_type": "integer", "unit": "reviews"},
    ]
    return profile, responses


@pytest.fixture
def valid_ecommerce_records():
    profile = {
        "id": "22222222-2222-2222-2222-222222222222",
        "name": "UrbanStyle D2C",
        "industry": "E-commerce",
        "location": "Austin, TX",
        "employee_count": 8,
    }
    responses = [
        {"question_id": "ecommerce.monthly_revenue", "value": "1200000", "numeric_value": 1200000.0, "data_type": "currency", "unit": "₹ / $"},
        {"question_id": "ecommerce.monthly_expenses", "value": "900000", "numeric_value": 900000.0, "data_type": "currency", "unit": "₹ / $"},
        {"question_id": "ecommerce.gross_margin_percentage", "value": "55.0", "numeric_value": 55.0, "data_type": "percentage", "unit": "%"},
        {"question_id": "ecommerce.monthly_orders", "value": "2400", "numeric_value": 2400.0, "data_type": "integer", "unit": "orders"},
        {"question_id": "ecommerce.repeat_purchase_percentage", "value": "30.0", "numeric_value": 30.0, "data_type": "percentage", "unit": "%"},
        {"question_id": "ecommerce.average_order_value", "value": "500", "numeric_value": 500.0, "data_type": "currency", "unit": "₹ / $"},
        {"question_id": "ecommerce.return_rate_percentage", "value": "6.5", "numeric_value": 6.5, "data_type": "percentage", "unit": "%"},
        {"question_id": "ecommerce.monthly_marketing_spend", "value": "150000", "numeric_value": 150000.0, "data_type": "currency", "unit": "₹ / $"},
        {"question_id": "ecommerce.customer_acquisition_cost", "value": "180", "numeric_value": 180.0, "data_type": "currency", "unit": "₹ / $"},
        {"question_id": "ecommerce.monthly_website_traffic", "value": "80000", "numeric_value": 80000.0, "data_type": "integer", "unit": "visitors"},
        {"question_id": "ecommerce.conversion_rate", "value": "3.0", "numeric_value": 3.0, "data_type": "percentage", "unit": "%"},
    ]
    return profile, responses


def test_valid_restaurant_pipeline(valid_restaurant_records):
    """Verifies complete end-to-end processing for a valid restaurant entity."""
    profile, responses = valid_restaurant_records
    extracted = DataExtractor.from_records(profile, responses)
    pipeline = DataEngineeringPipeline()
    output = pipeline.run(extracted)

    assert output.business_id == "11111111-1111-1111-1111-111111111111"
    assert output.industry == "Restaurant"
    assert len(output.validation_errors) == 0

    # Cleaned metrics checks
    assert "monthly_revenue" in output.cleaned_metrics
    assert output.cleaned_metrics["monthly_revenue"]["value"] == 500000.0
    assert output.cleaned_metrics["monthly_revenue"]["status"] == "valid"

    # Derived features checks
    features = output.derived_features
    assert "operating_profit" in features
    assert features["operating_profit"]["value"] == 150000.0
    assert features["operating_profit"]["status"] == "computed"
    assert features["operating_profit"]["source_inputs"] == ["monthly_revenue", "monthly_expenses"]

    assert "operating_margin" in features
    assert features["operating_margin"]["value"] == 30.0  # (150000 / 500000) * 100
    assert features["operating_margin"]["unit"] == "%"

    assert "calculated_average_order_value" in features
    assert features["calculated_average_order_value"]["value"] == 500.0  # 500000 / 1000

    assert "revenue_per_employee" in features
    assert features["revenue_per_employee"]["value"] == round(500000.0 / 12, 2)

    assert "revenue_per_table" in features
    assert features["revenue_per_table"]["value"] == 20000.0  # 500000 / 25


def test_valid_ecommerce_pipeline(valid_ecommerce_records):
    """Verifies complete end-to-end processing for a valid e-commerce entity."""
    profile, responses = valid_ecommerce_records
    extracted = DataExtractor.from_records(profile, responses)
    pipeline = DataEngineeringPipeline()
    output = pipeline.run(extracted)

    assert output.business_id == "22222222-2222-2222-2222-222222222222"
    assert len(output.validation_errors) == 0

    features = output.derived_features
    assert features["operating_profit"]["value"] == 300000.0  # 1200000 - 900000
    assert features["operating_margin"]["value"] == 25.0      # (300000 / 1200000) * 100
    assert features["revenue_per_visitor"]["value"] == 15.0   # 1200000 / 80000
    assert features["orders_per_visitor"]["value"] == 0.03    # 2400 / 80000
    assert features["cac_to_aov_ratio"]["value"] == 0.36      # 180 / 500
    assert features["effective_return_impact"]["value"] == 78000.0  # 1200000 * 0.065


def test_missing_optional_metrics_not_replaced_with_zero(valid_restaurant_records):
    """
    Validates that missing optional metrics are marked as 'missing' with value=None,
    and are NOT silently replaced with zero.
    """
    profile, responses = valid_restaurant_records
    # Remove optional table_count and food_cost_percentage
    filtered_responses = [
        r for r in responses
        if r["question_id"] not in ("restaurant.table_count", "restaurant.food_cost_percentage")
    ]
    extracted = DataExtractor.from_records(profile, filtered_responses)
    pipeline = DataEngineeringPipeline()
    output = pipeline.run(extracted)

    # Errors should be empty because both fields are optional
    assert len(output.validation_errors) == 0

    # table_count must be None with status="missing", not 0
    table_m = output.cleaned_metrics["table_count"]
    assert table_m["value"] is None
    assert table_m["status"] == "missing"

    # revenue_per_table feature should be skipped due to missing input, not zero
    assert output.derived_features["revenue_per_table"]["status"] == "skipped_missing_input"
    assert output.derived_features["revenue_per_table"]["value"] is None


def test_invalid_numeric_values_rejected(valid_restaurant_records):
    """Ensures non-numeric strings or negative currency values fail validation."""
    profile, responses = valid_restaurant_records
    for r in responses:
        if r["question_id"] == "restaurant.monthly_revenue":
            r["value"] = "-50000"
            r["numeric_value"] = -50000.0

    extracted = DataExtractor.from_records(profile, responses)
    pipeline = DataEngineeringPipeline()
    output = pipeline.run(extracted)

    assert len(output.validation_errors) > 0
    assert any("monthly_revenue" in err for err in output.validation_errors)
    assert output.cleaned_metrics["monthly_revenue"]["status"] == "invalid"


def test_percentage_bounds_enforced(valid_restaurant_records):
    """Ensures percentages greater than 100% or less than 0% are flagged as errors."""
    profile, responses = valid_restaurant_records
    for r in responses:
        if r["question_id"] == "restaurant.repeat_customer_percentage":
            r["value"] = "125.0"
            r["numeric_value"] = 125.0

    extracted = DataExtractor.from_records(profile, responses)
    pipeline = DataEngineeringPipeline()
    output = pipeline.run(extracted)

    assert any("percentage_bound" in err or "125.0" in err for err in output.validation_errors)
    assert output.cleaned_metrics["repeat_customer_percentage"]["status"] == "invalid"


def test_division_by_zero_safety(valid_restaurant_records):
    """
    Validates that zero orders, zero revenue, or zero employees are handled safely
    without throwing ZeroDivisionError, returning status='skipped_zero_division'.
    """
    profile, responses = valid_restaurant_records
    for r in responses:
        if r["question_id"] == "restaurant.monthly_orders":
            r["value"] = "0"
            r["numeric_value"] = 0.0
        elif r["question_id"] == "restaurant.employee_count":
            r["value"] = "0"
            r["numeric_value"] = 0.0

    extracted = DataExtractor.from_records(profile, responses)
    pipeline = DataEngineeringPipeline()
    # Must not raise ZeroDivisionError
    output = pipeline.run(extracted)

    calc_aov = output.derived_features["calculated_average_order_value"]
    assert calc_aov["status"] == "skipped_zero_division"
    assert calc_aov["value"] is None

    rev_emp = output.derived_features["revenue_per_employee"]
    assert rev_emp["status"] == "skipped_zero_division"
    assert rev_emp["value"] is None


def test_incompatible_reporting_periods():
    """Validates that incompatible reporting periods (e.g. annual revenue) are detected."""
    profile = {"id": "test-id", "name": "Period Test", "industry": "Restaurant"}
    responses = [
        {
            "question_id": "restaurant.monthly_revenue",
            "value": "6000000",
            "period": "annual",  # Incompatible with expected monthly period
            "data_type": "currency",
        }
    ]
    extracted = DataExtractor.from_records(profile, responses)
    pipeline = DataEngineeringPipeline()
    output = pipeline.run(extracted)

    assert any("Incompatible reporting periods" in err for err in output.validation_errors)


def test_duplicate_question_identifiers_rejected(valid_restaurant_records):
    """Ensures duplicate responses for the same question ID generate validation errors."""
    profile, responses = valid_restaurant_records
    # Append a duplicate response
    responses.append({
        "question_id": "restaurant.monthly_revenue",
        "value": "999999",
        "data_type": "currency",
    })
    extracted = DataExtractor.from_records(profile, responses)
    pipeline = DataEngineeringPipeline()
    output = pipeline.run(extracted)

    assert any("Duplicate response found" in err for err in output.validation_errors)


def test_incompatible_industry_question_rejected(valid_restaurant_records):
    """Ensures an e-commerce question submitted for a restaurant is flagged."""
    profile, responses = valid_restaurant_records
    responses.append({
        "question_id": "ecommerce.conversion_rate",
        "value": "2.5",
        "data_type": "percentage",
    })
    extracted = DataExtractor.from_records(profile, responses)
    pipeline = DataEngineeringPipeline()
    output = pipeline.run(extracted)

    assert any("is not recognized for industry" in err for err in output.validation_errors)


def test_json_serialization(valid_restaurant_records):
    """Verifies that the PipelineOutput serializes cleanly to JSON."""
    profile, responses = valid_restaurant_records
    extracted = DataExtractor.from_records(profile, responses)
    pipeline = DataEngineeringPipeline()
    output = pipeline.run(extracted)

    dumped_dict = output.to_dict()
    # Must serialize with json.dumps without TypeError
    json_str = json.dumps(dumped_dict)
    assert isinstance(json_str, str)
    deserialized = json.loads(json_str)
    assert deserialized["business_id"] == "11111111-1111-1111-1111-111111111111"
    assert deserialized["pipeline_version"] == "0.1.0"


def test_deterministic_repeated_execution(valid_restaurant_records):
    """Verifies that executing the pipeline multiple times produces identical results."""
    profile, responses = valid_restaurant_records
    extracted = DataExtractor.from_records(profile, responses)
    pipeline = DataEngineeringPipeline()

    run_1 = pipeline.run(extracted).to_dict()
    run_2 = pipeline.run(extracted).to_dict()

    # Exclude timestamp for bitwise deterministic comparison
    run_1.pop("processing_timestamp")
    run_2.pop("processing_timestamp")

    assert run_1 == run_2


def test_scoring_interface_reserved():
    """
    Verifies that the scoring engine base class raises NotImplementedError,
    confirming that no scoring formula is implemented in Step 4.
    """
    class Step4Scorer(BaseScoringEngine):
        def evaluate(self, pipeline_output):
            return super().evaluate(pipeline_output)

    scorer = Step4Scorer()
    with pytest.raises(NotImplementedError):
        scorer.evaluate({})
