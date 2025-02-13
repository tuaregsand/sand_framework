import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import json
from datetime import datetime
import pytz

from api_gateway.main import app
from api_gateway.models import database, metrics
from api_gateway.core import security
from tests.utils.utils import random_string, random_email

@pytest.fixture
def test_user(db: Session):
    """Create a test user."""
    email = random_email()
    password = random_string()
    hashed_password = security.get_password_hash(password)
    
    db_user = database.User(
        email=email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user, password

@pytest.fixture
def test_project(db: Session, test_user):
    """Create a test project."""
    user, _ = test_user
    
    project = database.Project(
        name="Test Project",
        description="Test project for metrics",
        owner_id=user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project

@pytest.fixture
def test_contract(db: Session, test_project):
    """Create a test contract."""
    contract = database.Contract(
        name="Test Contract",
        source_code="""
        contract TestContract {
            uint256 private value;
            
            function setValue(uint256 newValue) public {
                value = newValue;
            }
            
            function getValue() public view returns (uint256) {
                return value;
            }
        }
        """,
        project_id=test_project.id
    )
    db.add(contract)
    db.commit()
    db.refresh(contract)
    
    return contract

@pytest.fixture
def test_metrics_result(db: Session, test_project, test_contract):
    """Create a test metrics result."""
    result = metrics.ContractMetricsResult(
        project_id=test_project.id,
        contract_id=test_contract.id,
        timestamp=datetime.now(pytz.UTC),
        loc_metrics={
            "total": 150,
            "code": 120,
            "comments": 20,
            "empty": 10,
            "comment_ratio": 16.67
        },
        complexity_metrics={
            "cyclomatic": {
                "total": 45,
                "average": 4.5,
                "max": 8
            },
            "cognitive": 25,
            "level": "medium"
        },
        inheritance_metrics={
            "max_depth": 2,
            "contracts": []
        },
        function_metrics={
            "total": 10,
            "avg_params": 1.5,
            "visibility": {
                "public": 5,
                "private": 3,
                "internal": 2,
                "external": 0
            }
        },
        variable_metrics={
            "total": 8,
            "by_type": {"uint256": 3, "address": 2, "bool": 3},
            "visibility": {
                "public": 2,
                "private": 4,
                "internal": 2
            }
        },
        dependency_metrics={
            "total": 3,
            "imports": ["@openzeppelin/contracts/token/ERC20/IERC20.sol"],
            "interfaces": ["IERC20"],
            "libraries": ["SafeMath"]
        }
    )
    
    # Calculate scores
    result.calculate_scores()
    
    db.add(result)
    db.commit()
    db.refresh(result)
    
    return result

def test_analyze_contract_metrics(
    client: TestClient,
    db: Session,
    test_user,
    test_contract
):
    """Test starting contract metrics analysis."""
    user, password = test_user
    
    # Login
    login_data = {
        "username": user.email,
        "password": password
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Start analysis
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        f"/metrics/analyze/{test_contract.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "metrics_id" in data
    assert data["status"] == "pending"

def test_get_metrics_result(
    client: TestClient,
    db: Session,
    test_user,
    test_metrics_result
):
    """Test retrieving metrics analysis result."""
    user, password = test_user
    
    # Login
    login_data = {
        "username": user.email,
        "password": password
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Get metrics result
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        f"/metrics/{test_metrics_result.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_metrics_result.id
    assert data["status"] == "completed"
    assert "metrics" in data
    assert "scores" in data
    
    # Verify metrics data
    metrics = data["metrics"]
    assert "loc" in metrics
    assert metrics["loc"]["total"] == 150
    assert "complexity" in metrics
    assert metrics["complexity"]["level"] == "medium"

def test_get_project_metrics(
    client: TestClient,
    db: Session,
    test_user,
    test_project,
    test_metrics_result
):
    """Test retrieving all metrics for a project."""
    user, password = test_user
    
    # Login
    login_data = {
        "username": user.email,
        "password": password
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Get project metrics
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(
        f"/metrics/project/{test_project.id}",
        headers=headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["project_id"] == test_project.id
    
    # Verify first result
    result = data[0]
    assert result["id"] == test_metrics_result.id
    assert "metrics" in result
    assert "scores" in result

def test_unauthorized_access(
    client: TestClient,
    db: Session,
    test_contract,
    test_metrics_result
):
    """Test unauthorized access to metrics endpoints."""
    # Try without auth token
    response = client.post(f"/metrics/analyze/{test_contract.id}")
    assert response.status_code == 401
    
    response = client.get(f"/metrics/{test_metrics_result.id}")
    assert response.status_code == 401
    
    # Create another user who doesn't own the project
    other_email = random_email()
    other_password = random_string()
    hashed_password = security.get_password_hash(other_password)
    
    other_user = database.User(
        email=other_email,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(other_user)
    db.commit()
    
    # Login as other user
    login_data = {
        "username": other_email,
        "password": other_password
    }
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    
    # Try to access resources
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        f"/metrics/analyze/{test_contract.id}",
        headers=headers
    )
    assert response.status_code == 403
    
    response = client.get(
        f"/metrics/{test_metrics_result.id}",
        headers=headers
    )
    assert response.status_code == 403
