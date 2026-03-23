import pytest
from httpx import ASGITransport, AsyncClient

import app.core.database as database
from app.core.config import get_settings
from app.core.security import create_access_token
from app.main import app


@pytest.fixture(autouse=True)
def _reset_db_client():
    """Reset the cached Motor client before each test so it binds to the current event loop."""
    database._client = None
    yield
    database._client = None


@pytest.fixture
def settings():
    return get_settings()


@pytest.fixture
def admin_token(settings):
    return create_access_token("test-admin-id", "admin", "fr", settings)


@pytest.fixture
def doctor_token(settings):
    return create_access_token("test-doctor-id", "doctor", "fr", settings)


@pytest.fixture
def patient_token(settings):
    return create_access_token("test-patient-id", "patient", "fr", settings)


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c
