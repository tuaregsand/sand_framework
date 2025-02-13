import re
import ast
from typing import List, Dict, Any
import logging
from pathlib import Path
import json
import asyncio

logger = logging.getLogger(__name__)

class CodeQualityChecker:
    """Analyzer for checking code quality and best practices in smart contracts."""
    
    def __init__(self):
        self.quality_patterns = self._load_quality_patterns()
        self.custom_rules = self._load_custom_rules()

    def _load_quality_patterns(self) -> Dict[str, Any]:
        """Load code quality patterns from JSON file."""
        try:
            patterns_path = Path(__file__).parent / "data" / "quality_patterns.json"
            with open(patterns_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading quality patterns: {str(e)}")
            return {}

    def _load_custom_rules(self) -> List[Dict[str, Any]]:
        """Load custom quality rules."""
        try:
            rules_path = Path(__file__).parent / "data" / "quality_rules.json"
            with open(rules_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading custom rules: {str(e)}")
            return []

    async def check(self, code: str) -> List[Dict[str, Any]]:
        """
        Check contract code for quality issues and best practices.
        
        Args:
            code: Smart contract source code
            
        Returns:
            List of quality issues found, each containing:
            - id: Unique identifier for the issue
            - name: Name of the issue
            - description: Detailed description
            - severity: Impact level (critical, high, medium, low, info)
            - line_number: Line number where issue was found
            - snippet: Code snippet containing the issue
            - recommendation: Suggested fix
        """
        issues = []
        
        try:
            # Run all checkers in parallel
            tasks = [
                self._check_documentation(code),
                self._check_naming_conventions(code),
                self._check_code_structure(code),
                self._check_error_handling(code),
                self._check_test_coverage(code),
                self._check_custom_rules(code)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Checker task failed: {str(result)}")
                    continue
                issues.extend(result)
            
            # Sort by severity
            severity_order = {
                "critical": 0,
                "high": 1,
                "medium": 2,
                "low": 3,
                "info": 4
            }
            issues.sort(key=lambda x: severity_order.get(x["severity"], 5))
            
            return issues
            
        except Exception as e:
            logger.error(f"Error in code quality check: {str(e)}")
            raise

    async def _check_documentation(self, code: str) -> List[Dict[str, Any]]:
        """Check for proper documentation."""
        issues = []
        
        patterns = [
            (
                r"function\s+\w+\s*\([^)]*\)[^{]*{(?![^}]*\/\/)",
                "Missing function documentation",
                "Function lacks documentation comments",
                "medium"
            ),
            (
                r"contract\s+\w+\s*{(?![^}]*\/\/)",
                "Missing contract documentation",
                "Contract lacks documentation header",
                "high"
            ),
        ]
        
        for pattern, name, desc, severity in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                issues.append({
                    "id": "DOC_ISSUE",
                    "name": name,
                    "description": desc,
                    "severity": severity,
                    "line_number": line_number,
                    "snippet": code[match.start():match.end()],
                    "recommendation": "Add proper documentation comments"
                })
        
        return issues

    async def _check_naming_conventions(self, code: str) -> List[Dict[str, Any]]:
        """Check for proper naming conventions."""
        issues = []
        
        patterns = [
            (
                r"function\s+[a-z]+[A-Z]",
                "Inconsistent function naming",
                "Function name should use camelCase",
                "low"
            ),
            (
                r"contract\s+[a-z]",
                "Improper contract naming",
                "Contract name should start with capital letter",
                "medium"
            ),
            (
                r"_\w+\s*=",
                "Private variable naming",
                "Private variables should not start with underscore",
                "low"
            ),
        ]
        
        for pattern, name, desc, severity in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                issues.append({
                    "id": "NAMING_ISSUE",
                    "name": name,
                    "description": desc,
                    "severity": severity,
                    "line_number": line_number,
                    "snippet": code[match.start():match.end()],
                    "recommendation": "Follow standard naming conventions"
                })
        
        return issues

    async def _check_code_structure(self, code: str) -> List[Dict[str, Any]]:
        """Check code structure and organization."""
        issues = []
        
        patterns = [
            (
                r"{[^}]{300,}",
                "Long function body",
                "Function body is too long",
                "medium"
            ),
            (
                r"if\s*\([^)]{100,}\)",
                "Complex condition",
                "Condition is too complex",
                "medium"
            ),
            (
                r"function\s+\w+\s*\([^)]{100,}\)",
                "Too many parameters",
                "Function has too many parameters",
                "high"
            ),
        ]
        
        for pattern, name, desc, severity in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                issues.append({
                    "id": "STRUCTURE_ISSUE",
                    "name": name,
                    "description": desc,
                    "severity": severity,
                    "line_number": line_number,
                    "snippet": code[match.start():match.end()],
                    "recommendation": "Break down into smaller components"
                })
        
        return issues

    async def _check_error_handling(self, code: str) -> List[Dict[str, Any]]:
        """Check for proper error handling."""
        issues = []
        
        patterns = [
            (
                r"require\s*\([^,)]+\)",
                "Missing error message",
                "Require statement without error message",
                "medium"
            ),
            (
                r"assert\s*\(",
                "Assert usage",
                "Assert used instead of require",
                "high"
            ),
            (
                r"revert\s*\(\)",
                "Generic revert",
                "Revert without specific error",
                "medium"
            ),
        ]
        
        for pattern, name, desc, severity in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                issues.append({
                    "id": "ERROR_HANDLING",
                    "name": name,
                    "description": desc,
                    "severity": severity,
                    "line_number": line_number,
                    "snippet": code[match.start():match.end()],
                    "recommendation": "Add specific error messages"
                })
        
        return issues

    async def _check_test_coverage(self, code: str) -> List[Dict[str, Any]]:
        """Check for test coverage indicators."""
        issues = []
        
        patterns = [
            (
                r"function\s+\w+\s*\([^)]*\)[^{]*{(?![^}]*test)",
                "Untested function",
                "No corresponding test found for function",
                "high"
            ),
            (
                r"contract\s+\w+\s*{(?![^}]*test)",
                "Untested contract",
                "No test file found for contract",
                "critical"
            ),
        ]
        
        for pattern, name, desc, severity in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                issues.append({
                    "id": "TEST_COVERAGE",
                    "name": name,
                    "description": desc,
                    "severity": severity,
                    "line_number": line_number,
                    "snippet": code[match.start():match.end()],
                    "recommendation": "Add comprehensive tests"
                })
        
        return issues

    async def _check_custom_rules(self, code: str) -> List[Dict[str, Any]]:
        """Apply custom quality rules."""
        issues = []
        
        for rule in self.custom_rules:
            try:
                pattern = rule["pattern"]
                matches = re.finditer(pattern, code)
                for match in matches:
                    line_number = code[:match.start()].count('\n') + 1
                    issues.append({
                        "id": rule["id"],
                        "name": rule["name"],
                        "description": rule["description"],
                        "severity": rule["severity"],
                        "line_number": line_number,
                        "snippet": code[match.start():match.end()],
                        "recommendation": rule["recommendation"]
                    })
            except Exception as e:
                logger.error(f"Error applying custom rule {rule.get('id')}: {str(e)}")
                continue
        
        return issues
