import os
from pathlib import Path
from dotenv import load_dotenv
import pytest
import sys
import ssl
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import asyncio
from typing import AsyncGenerator, Generator

# Load environment variables before any other imports
env_file = Path(__file__).parent.parent / ".env.test"
load_dotenv(env_file)
os.environ["TESTING"] = "true"

# Skip loading full app context for security scanner tests
if "test_security_scanner" in sys.argv[-1]:
    pass
else:
    from api_gateway.main import app
from api_gateway.db import Base, get_db
from api_gateway.models.database import User, Project, Contract, Analysis
from api_gateway.core.config import settings

# Create async engine for testing with proper SSL settings
test_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DB_ECHO,
    connect_args={
        "ssl": True,
        "ssl_context": ssl.create_default_context().set_ciphers("DEFAULT@SECLEVEL=1")
    }
)

# Create async session factory
TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

@pytest.fixture(scope="session", autouse=True)
def load_env():
    pass

@pytest.fixture(scope="session")
def test_data_dir():
    return Path(__file__).parent / "data"

@pytest.fixture(scope="session")
def sample_contract_path(test_data_dir):
    return test_data_dir / "sample_contract.rs"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Get a testing database session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture
def client(db) -> Generator:
    """Get a TestClient instance."""
    async def override_get_db():
        yield db

    if "test_security_scanner" not in sys.argv[-1]:
        app.dependency_overrides[get_db] = override_get_db
        with TestClient(app) as test_client:
            yield test_client
        app.dependency_overrides.clear()
    else:
        yield None

@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """Create a test user."""
    user = User(
        email="test@example.com",
        api_key="test_key",
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@pytest.fixture
async def test_project(db: AsyncSession, test_user: User) -> Project:
    """Create a test project."""
    project = Project(
        name="Test Project",
        description="Test project description",
        owner_id=test_user.id
    )
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project

@pytest.fixture
async def test_contract(db: AsyncSession, test_project: Project) -> Contract:
    """Create a test contract."""
    with open("tests/data/sample_contract.rs", "r") as f:
        source_code = f.read()
    
    contract = Contract(
        name="Test Contract",
        source_code=source_code,
        project_id=test_project.id
    )
    db.add(contract)
    await db.commit()
    await db.refresh(contract)
    return contract

@pytest.fixture
async def test_metrics_result(db: AsyncSession, test_contract: Contract) -> Analysis:
    """Create a test metrics analysis result."""
    analysis = Analysis(
        contract_id=test_contract.id,
        project_id=test_contract.project_id,
        analysis_type="metrics",
        status="completed",
        result={
            "complexity": 5,
            "lines_of_code": 100,
            "function_count": 10
        }
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    return analysis
