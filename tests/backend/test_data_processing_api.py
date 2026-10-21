"""
Stanleaf Backend API — Data Processing Integration Tests
========================================================
Integration tests for POST and GET /api/v1/businesses/{id}/data-processing.
"""

import sys
import uuid
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import app.models  # noqa: F401 - registers models
from app.main import app as fastapi_app
from app.core.database import Base, get_db

TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield
    fastapi_app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def restaurant_payload():
    return {
        "name": "Bistro Bella",
        "industry": "Restaurant",
        "location": "Chicago, IL",
        "website": "https://bistrobella.com",
        "business_age_years": 3,
        "revenue_range": "25L-50L",
        "employee_count": 12,
        "customer_count": 2200,
        "marketing_spend_monthly": 20000.0,
    }


@pytest.fixture
def ecommerce_payload():
    return {
        "name": "UrbanStyle D2C",
        "industry": "E-commerce",
        "location": "Austin, TX",
        "website": "https://urbanstyled2c.com",
        "business_age_years": 2,
        "revenue_range": "50L-1Cr",
        "employee_count": 8,
        "customer_count": 5000,
        "marketing_spend_monthly": 150000.0,
    }


@pytest.fixture
def restaurant_questionnaire_submission():
    return {
        "responses": [
            {"question_id": "restaurant.monthly_revenue", "value": 450000.0},
            {"question_id": "restaurant.monthly_expenses", "value": 315000.0},
            {"question_id": "restaurant.average_order_value", "value": 450.0},
            {"question_id": "restaurant.food_cost_percentage", "value": 31.0},
            {"question_id": "restaurant.monthly_customers", "value": 1000},
            {"question_id": "restaurant.repeat_customer_percentage", "value": 40.0},
            {"question_id": "restaurant.employee_count", "value": 10},
            {"question_id": "restaurant.monthly_orders", "value": 900},
            {"question_id": "restaurant.table_count", "value": 20},
            {"question_id": "restaurant.monthly_marketing_spend", "value": 18000.0},
            {"question_id": "restaurant.average_rating", "value": 4.5},
            {"question_id": "restaurant.total_reviews", "value": 280},
        ]
    }


@pytest.fixture
def ecommerce_questionnaire_submission():
    return {
        "responses": [
            {"question_id": "ecommerce.monthly_revenue", "value": 1500000.0},
            {"question_id": "ecommerce.monthly_expenses", "value": 1100000.0},
            {"question_id": "ecommerce.gross_margin_percentage", "value": 50.0},
            {"question_id": "ecommerce.monthly_orders", "value": 3000},
            {"question_id": "ecommerce.repeat_purchase_percentage", "value": 28.0},
            {"question_id": "ecommerce.average_order_value", "value": 500.0},
            {"question_id": "ecommerce.return_rate_percentage", "value": 5.0},
            {"question_id": "ecommerce.monthly_marketing_spend", "value": 200000.0},
            {"question_id": "ecommerce.customer_acquisition_cost", "value": 220.0},
            {"question_id": "ecommerce.monthly_website_traffic", "value": 100000},
            {"question_id": "ecommerce.conversion_rate", "value": 3.0},
        ]
    }


@pytest.mark.asyncio
async def test_data_processing_api_nonexistent_business_404():
    """Calling data-processing on a nonexistent business returns HTTP 404."""
    nonexistent_id = str(uuid.uuid4())
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        res = await client.post(f"/api/v1/businesses/{nonexistent_id}/data-processing")
        assert res.status_code == 404
        assert "not found" in res.json()["detail"].lower()


@pytest.mark.asyncio
async def test_data_processing_api_restaurant_flow(restaurant_payload, restaurant_questionnaire_submission):
    """
    Tests complete lifecycle:
    1. Create Restaurant profile
    2. Submit questionnaire responses
    3. Execute POST /businesses/{id}/data-processing
    4. Verify structured output and derived features
    """
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        # Step 1: Create Business
        biz_res = await client.post("/api/v1/businesses", json=restaurant_payload)
        assert biz_res.status_code == 201
        biz_id = biz_res.json()["id"]

        # Step 2: Submit Questionnaire
        q_res = await client.post(
            f"/api/v1/businesses/{biz_id}/questionnaire",
            json=restaurant_questionnaire_submission,
        )
        assert q_res.status_code == 201

        # Step 3: Run Data Processing
        dp_res = await client.post(f"/api/v1/businesses/{biz_id}/data-processing")
        assert dp_res.status_code == 200
        data = dp_res.json()

        # Step 4: Verify Structured Output
        assert data["business_id"] == biz_id
        assert data["industry"] == "Restaurant"
        assert len(data["validation_errors"]) == 0
        assert data["pipeline_version"] == "0.1.0"

        # Verify Cleaned Metrics
        cleaned = data["cleaned_metrics"]
        assert cleaned["monthly_revenue"]["value"] == 450000.0
        assert cleaned["monthly_expenses"]["value"] == 315000.0

        # Verify Derived Features
        features = data["derived_features"]
        assert features["operating_profit"]["value"] == 135000.0  # 450000 - 315000
        assert features["operating_margin"]["value"] == 30.0      # (135000 / 450000) * 100
        assert features["calculated_average_order_value"]["value"] == 500.0  # 450000 / 900
        assert features["revenue_per_employee"]["value"] == 45000.0  # 450000 / 10
        assert features["revenue_per_table"]["value"] == 22500.0     # 450000 / 20


@pytest.mark.asyncio
async def test_data_processing_api_ecommerce_flow(ecommerce_payload, ecommerce_questionnaire_submission):
    """
    Tests complete lifecycle for E-commerce business:
    1. Create E-commerce profile
    2. Submit questionnaire responses
    3. Execute POST /businesses/{id}/data-processing
    4. Verify structured output and derived features
    """
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        # Step 1: Create Business
        biz_res = await client.post("/api/v1/businesses", json=ecommerce_payload)
        assert biz_res.status_code == 201
        biz_id = biz_res.json()["id"]

        # Step 2: Submit Questionnaire
        q_res = await client.post(
            f"/api/v1/businesses/{biz_id}/questionnaire",
            json=ecommerce_questionnaire_submission,
        )
        assert q_res.status_code == 201

        # Step 3: Run Data Processing
        dp_res = await client.post(f"/api/v1/businesses/{biz_id}/data-processing")
        assert dp_res.status_code == 200
        data = dp_res.json()

        assert data["business_id"] == biz_id
        assert data["industry"] == "E-commerce"
        assert len(data["validation_errors"]) == 0

        features = data["derived_features"]
        assert features["operating_profit"]["value"] == 400000.0   # 1500000 - 1100000
        assert features["operating_margin"]["value"] == round((400000.0 / 1500000.0) * 100, 2)
        assert features["revenue_per_visitor"]["value"] == 15.0     # 1500000 / 100000
        assert features["orders_per_visitor"]["value"] == 0.03      # 3000 / 100000
        assert features["cac_to_aov_ratio"]["value"] == 0.44        # 220 / 500
        assert features["effective_return_impact"]["value"] == 75000.0  # 1500000 * 0.05


@pytest.mark.asyncio
async def test_data_processing_api_get_readonly(restaurant_payload, restaurant_questionnaire_submission):
    """GET /api/v1/businesses/{id}/data-processing returns read-only output matching POST."""
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        biz_res = await client.post("/api/v1/businesses", json=restaurant_payload)
        biz_id = biz_res.json()["id"]
        await client.post(f"/api/v1/businesses/{biz_id}/questionnaire", json=restaurant_questionnaire_submission)

        post_res = await client.post(f"/api/v1/businesses/{biz_id}/data-processing")
        get_res = await client.get(f"/api/v1/businesses/{biz_id}/data-processing")

        assert post_res.status_code == 200
        assert get_res.status_code == 200

        post_data = post_res.json()
        get_data = get_res.json()

        assert post_data["business_id"] == get_data["business_id"]
        assert post_data["derived_features"] == get_data["derived_features"]


@pytest.mark.asyncio
async def test_data_processing_api_without_questionnaire(restaurant_payload):
    """
    Running data-processing on a business that has NOT submitted a questionnaire yet
    returns 200 with structured validation errors indicating missing required metrics.
    """
    async with AsyncClient(transport=ASGITransport(app=fastapi_app), base_url="http://test") as client:
        biz_res = await client.post("/api/v1/businesses", json=restaurant_payload)
        biz_id = biz_res.json()["id"]

        dp_res = await client.post(f"/api/v1/businesses/{biz_id}/data-processing")
        assert dp_res.status_code == 200
        data = dp_res.json()

        assert len(data["validation_errors"]) > 0
        assert any("monthly_revenue" in err for err in data["validation_errors"])
        assert "restaurant.monthly_revenue" in data["missing_fields"]
