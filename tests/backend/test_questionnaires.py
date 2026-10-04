import sys
import uuid
from pathlib import Path
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

import app.models  # noqa: F401, E402 - registers models with Base.metadata
from app.main import app as fastapi_app  # noqa: E402
from app.core.database import Base, get_db  # noqa: E402

# Isolated SQLite in-memory database engine for test execution
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(autouse=True)
def setup_test_db():
    """Sets up a clean in-memory database schema before each test and drops it after."""
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
def valid_restaurant_payload():
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
def valid_restaurant_responses():
    return {
        "responses": [
            {"question_id": "restaurant.monthly_revenue", "value": 350000.0},
            {"question_id": "restaurant.monthly_expenses", "value": 240000.0},
            {"question_id": "restaurant.average_order_value", "value": 650.0},
            {"question_id": "restaurant.food_cost_percentage", "value": 32.0},
            {"question_id": "restaurant.monthly_customers", "value": 1800},
            {"question_id": "restaurant.repeat_customer_percentage", "value": 45.0},
            {"question_id": "restaurant.employee_count", "value": 12},
            {"question_id": "restaurant.monthly_orders", "value": 1500},
            {"question_id": "restaurant.table_count", "value": 24},
            {"question_id": "restaurant.monthly_marketing_spend", "value": 15000.0},
            {"question_id": "restaurant.average_rating", "value": 4.6},
            {"question_id": "restaurant.total_reviews", "value": 320},
        ]
    }


@pytest.mark.asyncio
async def test_restaurant_questionnaire_retrieval():
    """Test 1: Restaurant questionnaire retrieval returns 200 OK and ordered questions."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/questionnaires/restaurant")
        assert response.status_code == 200
        data = response.json()
        assert data["industry"] == "restaurant"
        assert len(data["questions"]) >= 8

        # Verify display order is monotonically increasing
        orders = [q["display_order"] for q in data["questions"]]
        assert orders == sorted(orders)

        question_ids = [q["id"] for q in data["questions"]]
        assert "restaurant.monthly_revenue" in question_ids
        assert "restaurant.average_rating" in question_ids


@pytest.mark.asyncio
async def test_ecommerce_questionnaire_retrieval():
    """Test 2: E-commerce questionnaire retrieval returns 200 OK and ordered questions."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/questionnaires/ecommerce")
        assert response.status_code == 200
        data = response.json()
        assert data["industry"] == "ecommerce"
        assert len(data["questions"]) >= 8

        question_ids = [q["id"] for q in data["questions"]]
        assert "ecommerce.monthly_revenue" in question_ids
        assert "ecommerce.conversion_rate" in question_ids


@pytest.mark.asyncio
async def test_unsupported_industry_returns_404():
    """Test 3: Requesting an unsupported industry returns 404 with error detail."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/questionnaires/aerospace")
        assert response.status_code == 404
        assert "Questionnaire not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_valid_questionnaire_submission(valid_restaurant_payload, valid_restaurant_responses):
    """Test 4: Submitting valid questionnaire responses returns 201 Created and persists records."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create business
        bus_res = await client.post("/api/v1/businesses", json=valid_restaurant_payload)
        assert bus_res.status_code == 201
        business_id = bus_res.json()["id"]

        # Submit questionnaire
        post_res = await client.post(
            f"/api/v1/businesses/{business_id}/questionnaire",
            json=valid_restaurant_responses,
        )
        assert post_res.status_code == 201
        data = post_res.json()
        assert data["business_id"] == business_id
        assert data["industry"] == "restaurant"
        assert data["responses_count"] == len(valid_restaurant_responses["responses"])
        assert len(data["responses"]) == len(valid_restaurant_responses["responses"])

        # Check numeric_value was populated correctly
        revenue_resp = next(
            r for r in data["responses"] if r["question_id"] == "restaurant.monthly_revenue"
        )
        assert revenue_resp["numeric_value"] == 350000.0


@pytest.mark.asyncio
async def test_invalid_business_id_returns_404(valid_restaurant_responses):
    """Test 5: Submitting questionnaire for nonexistent business ID returns 404."""
    transport = ASGITransport(app=fastapi_app)
    random_id = uuid.uuid4()
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post(
            f"/api/v1/businesses/{random_id}/questionnaire",
            json=valid_restaurant_responses,
        )
        assert response.status_code == 404
        assert f"Business with ID '{random_id}' not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_missing_required_response_rejected(valid_restaurant_payload, valid_restaurant_responses):
    """Test 6: Missing required responses are rejected with 422."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        bus_res = await client.post("/api/v1/businesses", json=valid_restaurant_payload)
        business_id = bus_res.json()["id"]

        # Remove required question 'restaurant.monthly_revenue'
        filtered_responses = [
            r for r in valid_restaurant_responses["responses"]
            if r["question_id"] != "restaurant.monthly_revenue"
        ]

        post_res = await client.post(
            f"/api/v1/businesses/{business_id}/questionnaire",
            json={"responses": filtered_responses},
        )
        assert post_res.status_code == 422
        assert "Missing required responses" in post_res.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_numeric_response_rejected(valid_restaurant_payload, valid_restaurant_responses):
    """Test 7: Negative numeric responses on min-constrained fields are rejected with 422."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        bus_res = await client.post("/api/v1/businesses", json=valid_restaurant_payload)
        business_id = bus_res.json()["id"]

        # Make monthly revenue negative
        bad_responses = [dict(r) for r in valid_restaurant_responses["responses"]]
        for r in bad_responses:
            if r["question_id"] == "restaurant.monthly_revenue":
                r["value"] = -50000.0

        post_res = await client.post(
            f"/api/v1/businesses/{business_id}/questionnaire",
            json={"responses": bad_responses},
        )
        assert post_res.status_code == 422
        assert "cannot be less than" in post_res.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_percentage_rejected(valid_restaurant_payload, valid_restaurant_responses):
    """Test 8: Invalid percentage (> 100 or < 0) is rejected with 422."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        bus_res = await client.post("/api/v1/businesses", json=valid_restaurant_payload)
        business_id = bus_res.json()["id"]

        # Make repeat customer percentage 125%
        bad_responses = [dict(r) for r in valid_restaurant_responses["responses"]]
        for r in bad_responses:
            if r["question_id"] == "restaurant.repeat_customer_percentage":
                r["value"] = 125.0

        post_res = await client.post(
            f"/api/v1/businesses/{business_id}/questionnaire",
            json={"responses": bad_responses},
        )
        assert post_res.status_code == 422
        assert "cannot exceed" in post_res.json()["detail"]


@pytest.mark.asyncio
async def test_invalid_question_id_rejected(valid_restaurant_payload, valid_restaurant_responses):
    """Test 9: Invalid/unrecognized question ID is rejected with 422."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        bus_res = await client.post("/api/v1/businesses", json=valid_restaurant_payload)
        business_id = bus_res.json()["id"]

        # Add a fabricated question ID
        bad_responses = [dict(r) for r in valid_restaurant_responses["responses"]]
        bad_responses.append({"question_id": "restaurant.flying_cars_count", "value": 10})

        post_res = await client.post(
            f"/api/v1/businesses/{business_id}/questionnaire",
            json={"responses": bad_responses},
        )
        assert post_res.status_code == 422
        assert "Invalid question ID" in post_res.json()["detail"]


@pytest.mark.asyncio
async def test_retrieve_stored_questionnaire_responses(valid_restaurant_payload, valid_restaurant_responses):
    """Test 10: Stored responses can be retrieved via GET endpoint."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        bus_res = await client.post("/api/v1/businesses", json=valid_restaurant_payload)
        business_id = bus_res.json()["id"]

        # Before submission -> empty list
        get_initial = await client.get(f"/api/v1/businesses/{business_id}/questionnaire")
        assert get_initial.status_code == 200
        assert get_initial.json() == []

        # Submit
        await client.post(
            f"/api/v1/businesses/{business_id}/questionnaire",
            json=valid_restaurant_responses,
        )

        # After submission -> all records returned
        get_after = await client.get(f"/api/v1/businesses/{business_id}/questionnaire")
        assert get_after.status_code == 200
        data = get_after.json()
        assert len(data) == len(valid_restaurant_responses["responses"])
        q_ids = [r["question_id"] for r in data]
        assert "restaurant.monthly_revenue" in q_ids
        assert "restaurant.average_rating" in q_ids
