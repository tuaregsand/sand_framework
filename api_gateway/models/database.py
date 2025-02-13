from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, UTC

from api_gateway.db import Base
from api_gateway.models.schemas import ContractFramework, AnalysisStatus, SecuritySeverity

# Configure naming convention for Base.metadata
Base.metadata.naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    api_key = Column(String, unique=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    projects = relationship("Project", back_populates="owner")
    alerts = relationship("Alert", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    framework = Column(SQLEnum(ContractFramework))
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    owner = relationship("User", back_populates="projects")
    analyses = relationship("Analysis", back_populates="project")
    contracts = relationship("Contract", back_populates="project")

class Contract(Base):
    __tablename__ = "contracts"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String, index=True)
    source_code = Column(String)
    bytecode = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    project = relationship("Project", back_populates="contracts")
    analyses = relationship("Analysis", back_populates="contract")

class Analysis(Base):
    __tablename__ = "analyses"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING)
    results = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    contract = relationship("Contract", back_populates="analyses")
    project = relationship("Project", back_populates="analyses")
    security_issues = relationship("SecurityIssue", back_populates="analysis")
    gas_optimizations = relationship("GasOptimization", back_populates="analysis")

class SecurityIssue(Base):
    __tablename__ = "security_issues"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    type = Column(String, index=True)
    severity = Column(SQLEnum(SecuritySeverity))
    description = Column(String)
    location = Column(JSON)  # Stores file, line number, etc.
    recommendation = Column(String)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    analysis = relationship("Analysis", back_populates="security_issues")

class GasOptimization(Base):
    __tablename__ = "gas_optimizations"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    type = Column(String, index=True)
    description = Column(String)
    location = Column(JSON)  # Stores file, line number, etc.
    estimated_savings = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))

    analysis = relationship("Analysis", back_populates="gas_optimizations")

class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String, index=True)
    severity = Column(SQLEnum(SecuritySeverity))
    message = Column(String)
    alert_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    user = relationship("User", back_populates="alerts")
