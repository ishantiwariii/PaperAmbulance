import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import Base, get_db
from app.core.security import get_current_user

# --- DATABASE SETUP (SQLite in-memory for testing) ---
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def db():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

# --- SECURITY MOCK ---
@pytest.fixture
def mock_user_auth():
    """Returns a mock user payload as returned by Clerk/Neon Auth."""
    return {"sub": "test_user_unique_id", "email": "test@example.com"}

@pytest.fixture
def authenticated_client(client, mock_user_auth):
    """Overrides security dependency to return a mock user."""
    app.dependency_overrides[get_current_user] = lambda: mock_user_auth
    yield client
    app.dependency_overrides.pop(get_current_user)
