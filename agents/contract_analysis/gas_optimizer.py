import re
import ast
from typing import List, Dict, Any
import logging
from pathlib import Path
import json
import asyncio

logger = logging.getLogger(__name__)

class GasOptimizer:
    """Analyzer for identifying gas optimization opportunities in smart contracts."""
    
    def __init__(self):
        self.optimization_patterns = self._load_optimization_patterns()
        self.custom_rules = self._load_custom_rules()

    def _load_optimization_patterns(self) -> Dict[str, Any]:
        """Load gas optimization patterns from JSON file."""
        try:
            patterns_path = Path(__file__).parent / "data" / "gas_patterns.json"
            with open(patterns_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading optimization patterns: {str(e)}")
            return {}

    def _load_custom_rules(self) -> List[Dict[str, Any]]:
        """Load custom optimization rules."""
        try:
            rules_path = Path(__file__).parent / "data" / "gas_rules.json"
            with open(rules_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading custom rules: {str(e)}")
            return []

    async def analyze(self, code: str) -> List[Dict[str, Any]]:
        """
        Analyze contract code for gas optimization opportunities.
        
        Args:
            code: Smart contract source code
            
        Returns:
            List of optimization suggestions, each containing:
            - id: Unique identifier for the optimization
            - name: Name of the optimization
            - description: Detailed description
            - severity: Impact level (high, medium, low)
            - line_number: Line number where optimization is possible
            - snippet: Code snippet that can be optimized
            - recommendation: Suggested optimization
            - estimated_savings: Estimated gas savings
        """
        optimizations = []
        
        try:
            # Run all analyzers in parallel
            tasks = [
                self._analyze_storage_patterns(code),
                self._analyze_loops(code),
                self._analyze_function_modifiers(code),
                self._analyze_data_types(code),
                self._analyze_memory_usage(code),
                self._analyze_custom_rules(code)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Analyzer task failed: {str(result)}")
                    continue
                optimizations.extend(result)
            
            # Sort by estimated savings
            optimizations.sort(
                key=lambda x: x.get("estimated_savings", 0),
                reverse=True
            )
            
            return optimizations
            
        except Exception as e:
            logger.error(f"Error in gas optimization analysis: {str(e)}")
            raise

    async def _analyze_storage_patterns(self, code: str) -> List[Dict[str, Any]]:
        """Analyze storage access patterns for optimization."""
        optimizations = []
        
        patterns = [
            (
                r"storage\s+\w+\s*=\s*\w+",
                "Multiple storage reads",
                "Cache storage variables in memory for multiple reads",
                "high",
                2000
            ),
            (
                r"mapping\(address\s*=>\s*\w+\)",
                "Unoptimized mapping",
                "Consider using uint256 keys instead of address for mappings",
                "medium",
                1000
            ),
        ]
        
        for pattern, name, desc, severity, savings in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                optimizations.append({
                    "id": "STORAGE_OPT",
                    "name": name,
                    "description": desc,
                    "severity": severity,
                    "line_number": line_number,
                    "snippet": code[match.start():match.end()],
                    "recommendation": "Cache storage variables in memory",
                    "estimated_savings": savings
                })
        
        return optimizations

    async def _analyze_loops(self, code: str) -> List[Dict[str, Any]]:
        """Analyze loop constructs for optimization."""
        optimizations = []
        
        patterns = [
            (
                r"for\s*\([^;]*;\s*[^;]*length[^;]*;",
                "Array length in loop",
                "Array length is accessed in every iteration",
                "high",
                3000
            ),
            (
                r"while\s*\([^)]*\)\s*{[^}]*storage",
                "Storage access in loop",
                "Storage variable accessed in loop",
                "high",
                2500
            ),
        ]
        
        for pattern, name, desc, severity, savings in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                optimizations.append({
                    "id": "LOOP_OPT",
                    "name": name,
                    "description": desc,
                    "severity": severity,
                    "line_number": line_number,
                    "snippet": code[match.start():match.end()],
                    "recommendation": "Cache array length outside loop",
                    "estimated_savings": savings
                })
        
        return optimizations

    async def _analyze_function_modifiers(self, code: str) -> List[Dict[str, Any]]:
        """Analyze function modifiers for optimization."""
        optimizations = []
        
        patterns = [
            (
                r"function\s+\w+\s*\([^)]*\)\s*public\s+view",
                "Public view function",
                "Consider using external instead of public for view functions",
                "medium",
                500
            ),
            (
                r"modifier\s+\w+[^{]*{[^}]*storage",
                "Storage in modifier",
                "Storage access in modifier",
                "high",
                2000
            ),
        ]
        
        for pattern, name, desc, severity, savings in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                optimizations.append({
                    "id": "MODIFIER_OPT",
                    "name": name,
                    "description": desc,
                    "severity": severity,
                    "line_number": line_number,
                    "snippet": code[match.start():match.end()],
                    "recommendation": "Use external visibility for view functions",
                    "estimated_savings": savings
                })
        
        return optimizations

    async def _analyze_data_types(self, code: str) -> List[Dict[str, Any]]:
        """Analyze data type usage for optimization."""
        optimizations = []
        
        patterns = [
            (
                r"uint8|uint16|uint32",
                "Small uint types",
                "Smaller uint types may cost more gas",
                "medium",
                1000
            ),
            (
                r"string\s+storage",
                "String storage",
                "Consider using bytes instead of string",
                "medium",
                1500
            ),
        ]
        
        for pattern, name, desc, severity, savings in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                optimizations.append({
                    "id": "DATATYPE_OPT",
                    "name": name,
                    "description": desc,
                    "severity": severity,
                    "line_number": line_number,
                    "snippet": code[match.start():match.end()],
                    "recommendation": "Use uint256 or bytes where possible",
                    "estimated_savings": savings
                })
        
        return optimizations

    async def _analyze_memory_usage(self, code: str) -> List[Dict[str, Any]]:
        """Analyze memory usage patterns for optimization."""
        optimizations = []
        
        patterns = [
            (
                r"memory\s+\w+\s*\[\s*\]",
                "Dynamic memory array",
                "Dynamic memory arrays can be gas intensive",
                "high",
                2000
            ),
            (
                r"new\s+\w+\s*\[\s*\]",
                "Dynamic array creation",
                "Dynamic array creation in function",
                "high",
                2500
            ),
        ]
        
        for pattern, name, desc, severity, savings in patterns:
            matches = re.finditer(pattern, code)
            for match in matches:
                line_number = code[:match.start()].count('\n') + 1
                optimizations.append({
                    "id": "MEMORY_OPT",
                    "name": name,
                    "description": desc,
                    "severity": severity,
                    "line_number": line_number,
                    "snippet": code[match.start():match.end()],
                    "recommendation": "Use fixed size arrays where possible",
                    "estimated_savings": savings
                })
        
        return optimizations

    async def _analyze_custom_rules(self, code: str) -> List[Dict[str, Any]]:
        """Apply custom optimization rules."""
        optimizations = []
        
        for rule in self.custom_rules:
            try:
                pattern = rule["pattern"]
                matches = re.finditer(pattern, code)
                for match in matches:
                    line_number = code[:match.start()].count('\n') + 1
                    optimizations.append({
                        "id": rule["id"],
                        "name": rule["name"],
                        "description": rule["description"],
                        "severity": rule["severity"],
                        "line_number": line_number,
                        "snippet": code[match.start():match.end()],
                        "recommendation": rule["recommendation"],
                        "estimated_savings": rule.get("estimated_savings", 0)
                    })
            except Exception as e:
                logger.error(f"Error applying custom rule {rule.get('id')}: {str(e)}")
                continue
        
        return optimizations
