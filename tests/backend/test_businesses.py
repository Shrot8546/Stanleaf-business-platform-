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
def valid_business_payload():
    return {
        "name": "Acme Analytics Inc",
        "industry": "Software & AI",
        "location": "San Francisco, CA",
        "website": "https://acmeanalytics.io",
        "business_age_years": 4,
        "revenue_range": "25L-50L",
        "employee_count": 22,
        "customer_count": 3500,
        "marketing_spend_monthly": 45000.0,
    }


@pytest.mark.asyncio
async def test_create_valid_business(valid_business_payload):
    """Test 1: Creating a valid business entity returns 201 Created and persists all fields."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/businesses", json=valid_business_payload)
        assert response.status_code == 201, response.text
        data = response.json()

        # Validate generated UUID & timestamps
        assert "id" in data
        assert uuid.UUID(data["id"])  # Valid UUID format
        assert "created_at" in data
        assert "updated_at" in data

        # Validate submitted payload values match
        assert data["name"] == valid_business_payload["name"]
        assert data["industry"] == valid_business_payload["industry"]
        assert data["location"] == valid_business_payload["location"]
        assert data["website"] == valid_business_payload["website"]
        assert data["business_age_years"] == valid_business_payload["business_age_years"]
        assert data["revenue_range"] == valid_business_payload["revenue_range"]
        assert data["employee_count"] == valid_business_payload["employee_count"]
        assert data["customer_count"] == valid_business_payload["customer_count"]
        assert data["marketing_spend_monthly"] == valid_business_payload["marketing_spend_monthly"]


@pytest.mark.asyncio
async def test_reject_invalid_business_data():
    """Test 2: Rejecting invalid business data with appropriate HTTP 422 errors."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Case A: Missing required fields
        res_missing = await client.post("/api/v1/businesses", json={"name": "Only Name"})
        assert res_missing.status_code == 422

        # Case B: Empty string / whitespace for required fields
        res_blank = await client.post(
            "/api/v1/businesses",
            json={
                "name": "   ",
                "industry": "Tech",
                "location": "Austin",
            },
        )
        assert res_blank.status_code == 422

        # Case C: Negative business_age_years
        res_neg_age = await client.post(
            "/api/v1/businesses",
            json={
                "name": "Test Co",
                "industry": "Retail",
                "location": "New York",
                "business_age_years": -3,
            },
        )
        assert res_neg_age.status_code == 422

        # Case D: Negative employee_count
        res_neg_emp = await client.post(
            "/api/v1/businesses",
            json={
                "name": "Test Co",
                "industry": "Retail",
                "location": "New York",
                "employee_count": -10,
            },
        )
        assert res_neg_emp.status_code == 422

        # Case E: Negative customer_count
        res_neg_cust = await client.post(
            "/api/v1/businesses",
            json={
                "name": "Test Co",
                "industry": "Retail",
                "location": "New York",
                "customer_count": -5,
            },
        )
        assert res_neg_cust.status_code == 422

        # Case F: Negative marketing spend
        res_neg_spend = await client.post(
            "/api/v1/businesses",
            json={
                "name": "Test Co",
                "industry": "Retail",
                "location": "New York",
                "marketing_spend_monthly": -500.0,
            },
        )
        assert res_neg_spend.status_code == 422

        # Case G: Invalid website format
        res_bad_url = await client.post(
            "/api/v1/businesses",
            json={
                "name": "Test Co",
                "industry": "Retail",
                "location": "New York",
                "website": "this is not a url",
            },
        )
        assert res_bad_url.status_code == 422


@pytest.mark.asyncio
async def test_retrieve_business(valid_business_payload):
    """Test 3: Retrieving an existing business by UUID returns 200 OK."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create business
        post_res = await client.post("/api/v1/businesses", json=valid_business_payload)
        assert post_res.status_code == 201
        created_id = post_res.json()["id"]

        # Retrieve business
        get_res = await client.get(f"/api/v1/businesses/{created_id}")
        assert get_res.status_code == 200
        retrieved = get_res.json()
        assert retrieved["id"] == created_id
        assert retrieved["name"] == valid_business_payload["name"]


@pytest.mark.asyncio
async def test_retrieve_nonexistent_business_404():
    """Test 4: Retrieving a nonexistent business ID returns 404 with clear message."""
    transport = ASGITransport(app=fastapi_app)
    random_id = uuid.uuid4()
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(f"/api/v1/businesses/{random_id}")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert f"Business with ID '{random_id}' not found" in data["detail"]


@pytest.mark.asyncio
async def test_list_businesses(valid_business_payload):
    """Test 5: Listing businesses returns 200 OK and all registered businesses."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Initially empty
        initial_res = await client.get("/api/v1/businesses")
        assert initial_res.status_code == 200
        assert initial_res.json() == []

        # Create two businesses
        payload1 = valid_business_payload.copy()
        payload1["name"] = "Business Alpha"

        payload2 = valid_business_payload.copy()
        payload2["name"] = "Business Beta"

        await client.post("/api/v1/businesses", json=payload1)
        await client.post("/api/v1/businesses", json=payload2)

        # Retrieve list
        list_res = await client.get("/api/v1/businesses")
        assert list_res.status_code == 200
        businesses = list_res.json()
        assert len(businesses) == 2
        names = [b["name"] for b in businesses]
        assert "Business Alpha" in names
        assert "Business Beta" in names
