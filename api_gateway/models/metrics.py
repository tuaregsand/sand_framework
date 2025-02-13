from sqlalchemy import Column, Integer, String, Float, JSON, ForeignKey, DateTime, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import pytz

from .database import Base

class ContractMetricsResult(Base):
    """Model for storing smart contract metrics analysis results."""
    
    __tablename__ = "contract_metrics_results"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))

    # Metrics data stored as JSON
    loc_metrics = Column(JSON, nullable=False)
    complexity_metrics = Column(JSON, nullable=False)
    inheritance_metrics = Column(JSON, nullable=False)
    function_metrics = Column(JSON, nullable=False)
    variable_metrics = Column(JSON, nullable=False)
    dependency_metrics = Column(JSON, nullable=False)

    # Summary scores (0-100)
    maintainability_score = Column(Float)
    complexity_score = Column(Float)
    security_score = Column(Float)
    gas_efficiency_score = Column(Float)
    overall_score = Column(Float)

    # Relationships
    project = relationship("Project", back_populates="metrics_results")
    contract = relationship("Contract", back_populates="metrics_results")

    # Indexes for efficient querying
    __table_args__ = (
        Index("idx_metrics_project", "project_id"),
        Index("idx_metrics_contract", "contract_id"),
        Index("idx_metrics_timestamp", "timestamp"),
    )

    def calculate_scores(self):
        """Calculate summary scores based on individual metrics."""
        try:
            # Maintainability score based on LOC and complexity
            self.maintainability_score = self._calculate_maintainability_score()
            
            # Complexity score based on cyclomatic and cognitive complexity
            self.complexity_score = self._calculate_complexity_score()
            
            # Security score based on visibility and inheritance metrics
            self.security_score = self._calculate_security_score()
            
            # Gas efficiency score based on function metrics
            self.gas_efficiency_score = self._calculate_gas_efficiency_score()
            
            # Overall weighted score
            self.overall_score = (
                self.maintainability_score * 0.3 +
                self.complexity_score * 0.2 +
                self.security_score * 0.3 +
                self.gas_efficiency_score * 0.2
            )
            
        except Exception as e:
            # Log error but don't fail - scores will remain null
            logger.error(f"Error calculating metrics scores: {str(e)}")

    def _calculate_maintainability_score(self) -> float:
        """Calculate maintainability score (0-100)."""
        try:
            # Factors affecting maintainability:
            # 1. Comment ratio (higher is better)
            comment_ratio = self.loc_metrics.get("comment_ratio", 0)
            comment_score = min(100, comment_ratio * 3.33)  # 30% comments = 100
            
            # 2. Function length (lower is better)
            avg_function_length = self.function_metrics.get("avg_lines", 0)
            length_score = max(0, 100 - (avg_function_length - 15) * 2)  # -2 points per line over 15
            
            # 3. Dependencies (fewer is better)
            dep_count = self.dependency_metrics.get("total", 0)
            dep_score = max(0, 100 - dep_count * 5)  # -5 points per dependency
            
            # Weighted average
            return (comment_score * 0.4 + length_score * 0.4 + dep_score * 0.2)
            
        except Exception as e:
            logger.error(f"Error calculating maintainability score: {str(e)}")
            return 0.0

    def _calculate_complexity_score(self) -> float:
        """Calculate complexity score (0-100, higher is better/less complex)."""
        try:
            # 1. Cyclomatic complexity (lower is better)
            cyclomatic = self.complexity_metrics.get("cyclomatic", {})
            avg_complexity = cyclomatic.get("average", 0)
            complexity_score = max(0, 100 - avg_complexity * 5)  # -5 points per complexity point
            
            # 2. Cognitive complexity (lower is better)
            cognitive = self.complexity_metrics.get("cognitive", 0)
            cognitive_score = max(0, 100 - cognitive * 2)  # -2 points per cognitive complexity point
            
            # Equal weighting
            return (complexity_score * 0.5 + cognitive_score * 0.5)
            
        except Exception as e:
            logger.error(f"Error calculating complexity score: {str(e)}")
            return 0.0

    def _calculate_security_score(self) -> float:
        """Calculate security score (0-100)."""
        try:
            # 1. Visibility practices
            visibility = self.function_metrics.get("visibility", {})
            public_funcs = visibility.get("public", 0)
            private_funcs = visibility.get("private", 0) + visibility.get("internal", 0)
            visibility_ratio = private_funcs / (public_funcs + private_funcs) if (public_funcs + private_funcs) > 0 else 0
            visibility_score = visibility_ratio * 100  # Higher ratio of private/internal is better
            
            # 2. Inheritance depth (lower is better)
            max_depth = self.inheritance_metrics.get("max_depth", 0)
            inheritance_score = max(0, 100 - max_depth * 20)  # -20 points per inheritance level
            
            # 3. Variable visibility
            var_visibility = self.variable_metrics.get("visibility", {})
            public_vars = var_visibility.get("public", 0)
            private_vars = var_visibility.get("private", 0) + var_visibility.get("internal", 0)
            var_ratio = private_vars / (public_vars + private_vars) if (public_vars + private_vars) > 0 else 0
            var_score = var_ratio * 100
            
            # Weighted average
            return (visibility_score * 0.4 + inheritance_score * 0.3 + var_score * 0.3)
            
        except Exception as e:
            logger.error(f"Error calculating security score: {str(e)}")
            return 0.0

    def _calculate_gas_efficiency_score(self) -> float:
        """Calculate gas efficiency score (0-100)."""
        try:
            # 1. Function parameter count (fewer is better)
            avg_params = self.function_metrics.get("avg_params", 0)
            param_score = max(0, 100 - avg_params * 10)  # -10 points per average parameter
            
            # 2. External function ratio (more external is better for gas)
            visibility = self.function_metrics.get("visibility", {})
            external_funcs = visibility.get("external", 0)
            total_funcs = sum(visibility.values())
            external_ratio = external_funcs / total_funcs if total_funcs > 0 else 0
            external_score = external_ratio * 100
            
            # Equal weighting
            return (param_score * 0.5 + external_score * 0.5)
            
        except Exception as e:
            logger.error(f"Error calculating gas efficiency score: {str(e)}")
            return 0.0
