from pydantic import BaseModel, Field, validator
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any
from enum import Enum

class ContractFramework(str, Enum):
    ANCHOR = "anchor"
    SOLIDITY = "solidity"
    RUST = "rust"

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class SecuritySeverity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class PriceResponse(BaseModel):
    price_usd: float = Field(..., description="Current price in USD")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        json_schema_extra = {
            "example": {
                "price_usd": 123.45,
                "timestamp": "2025-02-12T18:43:58.123456+00:00"
            }
        }

class SentimentResponse(BaseModel):
    sentiment_score: float = Field(..., ge=-1, le=1, description="Sentiment score between -1 and 1")
    confidence: float = Field(..., ge=0, le=1, description="Confidence score of the sentiment analysis")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        json_schema_extra = {
            "example": {
                "sentiment_score": 0.75,
                "confidence": 0.95,
                "timestamp": "2025-02-12T18:43:58.123456+00:00"
            }
        }

class Alert(BaseModel):
    id: Optional[int] = None
    type: str = Field(..., description="Type of alert (e.g., 'price', 'security')")
    severity: SecuritySeverity
    message: str = Field(..., description="Alert message")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        json_schema_extra = {
            "example": {
                "type": "price",
                "severity": "high",
                "message": "SOL price increased by 10% in the last hour",
                "metadata": {"previous_price": 100, "current_price": 110},
                "timestamp": "2025-02-12T18:43:58.123456+00:00"
            }
        }

class DevQuestion(BaseModel):
    question: str = Field(..., min_length=10, description="Development question to ask")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        json_schema_extra = {
            "example": {
                "question": "How do I implement a token contract in Solana?",
                "context": {"framework": "anchor", "token_type": "fungible"}
            }
        }

class DevAnswer(BaseModel):
    answer: str = Field(..., description="Answer to the development question")
    references: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "To implement a token contract in Solana using Anchor...",
                "references": ["https://docs.solana.com/tokens"],
                "timestamp": "2025-02-12T18:43:58.123456+00:00"
            }
        }

class ProjectCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=10)
    framework: ContractFramework

    class Config:
        json_schema_extra = {
            "example": {
                "name": "my-token",
                "description": "A fungible token contract",
                "framework": "anchor"
            }
        }

class ProjectResult(BaseModel):
    result: str = Field(..., description="Result message")
    path: str = Field(..., description="Path to the created project")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        json_schema_extra = {
            "example": {
                "result": "Project created successfully",
                "path": "/path/to/project",
                "timestamp": "2025-02-12T18:43:58.123456+00:00"
            }
        }

class SecurityIssue(BaseModel):
    type: str = Field(..., description="Type of security issue")
    severity: SecuritySeverity
    description: str = Field(..., description="Detailed description of the issue")
    location: Dict[str, Any] = Field(..., description="Location in the code")
    recommendation: str = Field(..., description="How to fix the issue")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "reentrancy",
                "severity": "high",
                "description": "Potential reentrancy vulnerability in withdraw function",
                "location": {"file": "contract.sol", "line": 42},
                "recommendation": "Implement checks-effects-interactions pattern"
            }
        }

class GasOptimization(BaseModel):
    type: str = Field(..., description="Type of optimization")
    description: str = Field(..., description="Description of the optimization")
    location: Dict[str, Any] = Field(..., description="Location in the code")
    estimated_savings: int = Field(..., description="Estimated gas savings")

    class Config:
        json_schema_extra = {
            "example": {
                "type": "storage",
                "description": "Use uint128 instead of uint256",
                "location": {"file": "contract.sol", "line": 15},
                "estimated_savings": 5000
            }
        }

class AnalysisResult(BaseModel):
    security_issues: List[SecurityIssue] = Field(default_factory=list)
    gas_optimizations: List[GasOptimization] = Field(default_factory=list)
    code_quality: Dict[str, Any] = Field(...)
    metrics: Dict[str, Any] = Field(...)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Config:
        json_schema_extra = {
            "example": {
                "security_issues": [{
                    "type": "reentrancy",
                    "severity": "high",
                    "description": "Potential reentrancy vulnerability",
                    "location": {"file": "contract.sol", "line": 42},
                    "recommendation": "Implement checks-effects-interactions pattern"
                }],
                "gas_optimizations": [{
                    "type": "storage",
                    "description": "Use uint128 instead of uint256",
                    "location": {"file": "contract.sol", "line": 15},
                    "estimated_savings": 5000
                }],
                "code_quality": {
                    "complexity": {"score": 85, "issues": []},
                    "maintainability": {"score": 90, "issues": []}
                },
                "metrics": {
                    "loc": 150,
                    "functions": 10,
                    "complexity": "medium",
                    "inheritance_depth": 2
                },
                "timestamp": "2025-02-12T18:43:58.123456+00:00"
            }
        }

# Metrics schemas
class MetricsScores(BaseModel):
    maintainability: Optional[float]
    complexity: Optional[float]
    security: Optional[float]
    gas_efficiency: Optional[float]
    overall: Optional[float]

class MetricsData(BaseModel):
    loc: Dict[str, Any]
    complexity: Dict[str, Any]
    inheritance: Dict[str, Any]
    functions: Dict[str, Any]
    variables: Dict[str, Any]
    dependencies: Dict[str, Any]

class MetricsResult(BaseModel):
    id: int
    project_id: int
    contract_id: int
    timestamp: datetime
    status: str
    metrics: Optional[MetricsData]
    scores: Optional[MetricsScores]

    class Config:
        from_attributes = True

class MetricsResponse(BaseModel):
    status: str
    message: str
    metrics_id: int

class AnalysisResponse(BaseModel):
    """Response model for contract analysis."""
    analysis_id: int
    task_id: Optional[str] = None
    status: str
    results: Optional[Dict[str, Any]] = None
    task_status: Optional[Dict[str, Any]] = None

class ContractAnalysisResponse(BaseModel):
    analysis_id: int = Field(..., description="ID of the analysis")
    status: AnalysisStatus = Field(..., description="Status of the analysis")
    results: Optional[Dict[str, Any]] = Field(None, description="Analysis results if completed")

    class Config:
        json_schema_extra = {
            "example": {
                "analysis_id": 1,
                "status": "completed",
                "results": {
                    "metrics": {
                        "loc": 150,
                        "complexity": "medium"
                    },
                    "security": {
                        "issues": []
                    },
                    "gas": {
                        "optimizations": []
                    },
                    "quality": {
                        "score": 85
                    }
                }
            }
        }
