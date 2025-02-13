import os
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import logging
import ast
import re
from datetime import datetime, UTC

from .security_scanner import SecurityScanner
from .gas_optimizer import GasOptimizer
from .code_quality import CodeQualityChecker
from .metrics import ContractMetrics

logger = logging.getLogger(__name__)

@dataclass
class AnalysisResult:
    security_issues: List[Dict]
    gas_optimizations: List[Dict]
    code_quality_issues: List[Dict]
    metrics: Dict
    summary: str
    risk_score: float

class SmartContractAnalyzer:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.security_scanner = SecurityScanner()
        self.gas_optimizer = GasOptimizer()
        self.code_quality = CodeQualityChecker()
        self.metrics = ContractMetrics()
        
        # Load known vulnerabilities database
        self.vuln_db = self._load_vulnerability_database()
        
        # Load gas optimization patterns
        self.optimization_patterns = self._load_optimization_patterns()

    def _load_vulnerability_database(self) -> Dict[str, Any]:
        """Load known vulnerability patterns and descriptions."""
        try:
            db_path = Path(__file__).parent / "data" / "vulnerability_patterns.json"
            with open(db_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading vulnerability database: {str(e)}")
            return {}

    def _load_optimization_patterns(self) -> Dict[str, Any]:
        """Load gas optimization patterns."""
        try:
            patterns_path = Path(__file__).parent / "data" / "optimization_patterns.json"
            with open(patterns_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading optimization patterns: {str(e)}")
            return {}

    async def analyze(self) -> AnalysisResult:
        """
        Analyze the smart contract for security issues, gas optimizations,
        code quality, and metrics.
        """
        try:
            # Run security analysis
            security_issues = await self.security_scanner.scan(self.source_code)
            
            # Run gas optimization analysis
            gas_optimizations = await self.gas_optimizer.analyze(self.source_code)
            
            # Run code quality analysis
            code_quality_issues = await self.code_quality.check(self.source_code)
            
            # Compute metrics
            metrics = await self.metrics.compute(self.source_code)
            
            # Calculate risk score based on findings
            risk_score = self._calculate_risk_score(
                security_issues, gas_optimizations, code_quality_issues
            )
            
            # Generate summary
            summary = self._generate_summary(
                security_issues, gas_optimizations, code_quality_issues, metrics
            )
            
            return AnalysisResult(
                security_issues=security_issues,
                gas_optimizations=gas_optimizations,
                code_quality_issues=code_quality_issues,
                metrics=metrics,
                summary=summary,
                risk_score=risk_score
            )
            
        except Exception as e:
            logger.error(f"Error during contract analysis: {str(e)}")
            raise

    def _calculate_risk_score(
        self,
        security_issues: List[Dict],
        gas_optimizations: List[Dict],
        code_quality_issues: List[Dict]
    ) -> float:
        """Calculate a risk score based on the findings."""
        # Weight factors for different types of issues
        SECURITY_WEIGHT = 0.6
        GAS_WEIGHT = 0.2
        QUALITY_WEIGHT = 0.2
        
        # Calculate security score (0-10, higher is worse)
        security_score = min(len(security_issues) * 2, 10)
        
        # Calculate gas optimization score (0-10, higher is worse)
        gas_score = min(len(gas_optimizations), 10)
        
        # Calculate code quality score (0-10, higher is worse)
        quality_score = min(len(code_quality_issues), 10)
        
        # Calculate weighted average
        risk_score = (
            security_score * SECURITY_WEIGHT +
            gas_score * GAS_WEIGHT +
            quality_score * QUALITY_WEIGHT
        )
        
        return round(risk_score, 2)

    def _generate_summary(
        self,
        security_issues: List[Dict],
        gas_optimizations: List[Dict],
        code_quality_issues: List[Dict],
        metrics: Dict
    ) -> str:
        """Generate a human-readable summary of the analysis."""
        summary = []
        
        # Add security summary
        if security_issues:
            summary.append(
                f"Found {len(security_issues)} potential security issues. "
                "Review recommended."
            )
        else:
            summary.append("No security issues detected.")
            
        # Add gas optimization summary
        if gas_optimizations:
            summary.append(
                f"Found {len(gas_optimizations)} potential gas optimizations."
            )
        else:
            summary.append("No gas optimizations suggested.")
            
        # Add code quality summary
        if code_quality_issues:
            summary.append(
                f"Found {len(code_quality_issues)} code quality issues."
            )
        else:
            summary.append("No code quality issues found.")
            
        # Add metrics summary
        summary.append(
            f"Contract metrics: {metrics.get('lines_of_code', 0)} lines of code, "
            f"complexity score: {metrics.get('complexity', 0)}"
        )
        
        return " ".join(summary)

class SecurityScanner:
    async def scan(self, code: str) -> List[Dict[str, Any]]:
        """Scan contract for security vulnerabilities."""
        # Basic implementation
        issues = []
        
        # Check for common vulnerabilities
        if "selfdestruct" in code:
            issues.append({
                "type": "selfdestruct",
                "severity": "critical",
                "description": "Contract can be self-destructed",
                "line": code.find("selfdestruct")
            })
            
        if "delegatecall" in code:
            issues.append({
                "type": "delegatecall",
                "severity": "high",
                "description": "Dangerous delegatecall usage",
                "line": code.find("delegatecall")
            })
            
        return issues

class GasOptimizer:
    async def analyze(self, code: str) -> List[Dict[str, Any]]:
        """Analyze contract for gas optimizations."""
        # Basic implementation
        optimizations = []
        
        # Check for common gas optimization opportunities
        if "uint256" in code and not "uint128" in code:
            optimizations.append({
                "type": "data-size",
                "description": "Consider using uint128 instead of uint256 where possible",
                "estimated_savings": 5000,
                "line": code.find("uint256")
            })
            
        return optimizations

class CodeQualityChecker:
    async def check(self, code: str) -> List[Dict[str, Any]]:
        """Check code quality metrics."""
        # Basic implementation
        issues = []
        
        # Check for basic code quality issues
        if code.count("\n") > 1000:
            issues.append({
                "type": "file-size",
                "severity": "medium",
                "description": "File is too large, consider splitting into multiple files",
                "line": 1
            })
            
        return issues

class ContractMetrics:
    async def compute(self, code: str) -> Dict[str, Any]:
        """Compute general contract metrics."""
        # Basic implementation
        lines = code.split("\n")
        functions = [line for line in lines if "function" in line]
        
        return {
            "lines_of_code": len(lines),
            "functions": len(functions),
            "complexity": "medium" if len(functions) > 10 else "low",
            "inheritance_depth": code.count(" is ")
        }
