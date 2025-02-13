import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import os
import json
from datetime import datetime, timedelta

from api_gateway.main import app
from api_gateway.db import Base
from api_gateway.core.config import settings
from agents.web3_agent import Web3DevAgent
from agents.analytics_agent import AnalyticsAgent

# Test database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/test_db")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def test_db_session(test_db_engine):
    async_session = sessionmaker(
        test_db_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.fixture
async def test_client():
    async with AsyncClient(base_url="http://test") as client:
        app.dependency_overrides = {}  # Reset any overrides
        yield client

@pytest.mark.asyncio
async def test_full_analytics_flow(test_client, test_db_session):
    """Test the complete analytics flow."""
    # Test price endpoint
    response = await test_client.get("/analytics/price")
    assert response.status_code == 200
    price_data = response.json()
    assert "price_usd" in price_data
    assert "timestamp" in price_data

    # Test sentiment endpoint
    response = await test_client.get("/analytics/sentiment")
    assert response.status_code == 200
    sentiment_data = response.json()
    assert "sentiment_score" in sentiment_data
    assert "timestamp" in sentiment_data

@pytest.mark.asyncio
async def test_full_development_flow(test_client, test_db_session):
    """Test the complete development flow."""
    # Test project creation
    project_data = {
        "name": "test_project",
        "description": "Test smart contract project",
        "framework": "anchor"
    }
    response = await test_client.post("/dev/project/new", json=project_data)
    assert response.status_code == 200
    result = response.json()
    assert "result" in result
    assert "path" in result

    # Test development question
    question_data = {
        "question": "How do I implement a token contract?"
    }
    response = await test_client.post("/dev/ask", json=question_data)
    assert response.status_code == 200
    answer = response.json()
    assert "answer" in answer
    assert "timestamp" in answer

@pytest.mark.asyncio
async def test_system_integration(test_client, test_db_session):
    """Test system-wide integration."""
    # Test analytics integration with development
    price_response = await test_client.get("/analytics/price")
    assert price_response.status_code == 200
    
    question_data = {
        "question": f"What's the current SOL price?"
    }
    dev_response = await test_client.post("/dev/ask", json=question_data)
    assert dev_response.status_code == 200

@pytest.mark.asyncio
async def test_error_handling(test_client):
    """Test error handling across the system."""
    # Test invalid endpoint
    response = await test_client.get("/invalid")
    assert response.status_code == 404

    # Test invalid project creation
    invalid_project = {
        "name": "",  # Empty name should fail
        "description": "Test",
        "framework": "invalid"
    }
    response = await test_client.post("/dev/project/new", json=invalid_project)
    assert response.status_code in [400, 422]  # FastAPI validation error
