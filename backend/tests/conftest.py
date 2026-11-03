import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.config.settings import get_settings
from app.database.base import Base
from app.database.session import get_db

settings = get_settings()

@pytest.fixture(scope="session")
def engine():
    """Create a database engine connected to the target test/dev MySQL instance."""
    return create_engine(
        settings.database_url,
        pool_pre_ping=True,
    )

@pytest.fixture(scope="function")
def db_session(engine):
    """Provide a transactional database session for each test function."""
    connection = engine.connect()
    transaction = connection.begin()
    
    SessionLocal = sessionmaker(bind=connection, autocommit=False, autoflush=False)
    session = SessionLocal()

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with get_db dependency overridden to use the test session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
