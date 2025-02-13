import re
import ast
from typing import List, Dict, Any
import logging
from pathlib import Path
import json
import asyncio
import radon.metrics
from radon.visitors import ComplexityVisitor
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)

class ContractMetrics:
    """Analyzer for computing various metrics of smart contracts."""
    
    def __init__(self):
        self.metrics_config = self._load_metrics_config()

    def _load_metrics_config(self) -> Dict[str, Any]:
        """Load metrics configuration from JSON file."""
        try:
            config_path = Path(__file__).parent / "data" / "metrics_config.json"
            with open(config_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metrics config: {str(e)}")
            return {}

    async def calculate(self, code: str) -> Dict[str, Any]:
        """
        Calculate various metrics for the contract code.
        
        Args:
            code: Smart contract source code
            
        Returns:
            Dict containing various metrics:
            - loc: Lines of code metrics
            - complexity: Complexity metrics
            - inheritance: Inheritance metrics
            - functions: Function metrics
            - variables: Variable metrics
            - dependencies: Dependency metrics
        """
        try:
            # Run all metric calculations in parallel
            tasks = [
                self._calculate_loc_metrics(code),
                self._calculate_complexity_metrics(code),
                self._calculate_inheritance_metrics(code),
                self._calculate_function_metrics(code),
                self._calculate_variable_metrics(code),
                self._calculate_dependency_metrics(code)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            metrics = {}
            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Metrics calculation failed: {str(result)}")
                    continue
                metrics.update(result)
            
            # Add timestamp
            metrics["timestamp"] = datetime.now(pytz.UTC).isoformat()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating metrics: {str(e)}")
            raise

    async def _calculate_loc_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate lines of code metrics."""
        try:
            lines = code.split('\n')
            
            # Count different types of lines
            total_lines = len(lines)
            empty_lines = sum(1 for line in lines if not line.strip())
            comment_lines = sum(1 for line in lines if line.strip().startswith('//'))
            code_lines = total_lines - empty_lines - comment_lines
            
            return {
                "loc": {
                    "total": total_lines,
                    "code": code_lines,
                    "comments": comment_lines,
                    "empty": empty_lines,
                    "comment_ratio": round(comment_lines / total_lines * 100, 2) if total_lines > 0 else 0
                }
            }
        except Exception as e:
            logger.error(f"Error calculating LOC metrics: {str(e)}")
            return {"loc": {}}

    async def _calculate_complexity_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate complexity metrics."""
        try:
            # Calculate cyclomatic complexity
            complexity = ComplexityVisitor.from_code(code)
            functions = complexity.functions
            
            # Calculate cognitive complexity
            cognitive_complexity = self._calculate_cognitive_complexity(code)
            
            # Determine overall complexity level
            avg_complexity = sum(f.complexity for f in functions) / len(functions) if functions else 0
            complexity_level = (
                "high" if avg_complexity > 10 else
                "medium" if avg_complexity > 5 else
                "low"
            )
            
            return {
                "complexity": {
                    "cyclomatic": {
                        "total": sum(f.complexity for f in functions),
                        "average": round(avg_complexity, 2),
                        "max": max((f.complexity for f in functions), default=0),
                        "functions_by_complexity": [
                            {
                                "name": f.name,
                                "complexity": f.complexity,
                                "line_number": f.lineno
                            }
                            for f in sorted(functions, key=lambda x: x.complexity, reverse=True)
                        ]
                    },
                    "cognitive": cognitive_complexity,
                    "level": complexity_level
                }
            }
        except Exception as e:
            logger.error(f"Error calculating complexity metrics: {str(e)}")
            return {"complexity": {}}

    def _calculate_cognitive_complexity(self, code: str) -> int:
        """Calculate cognitive complexity."""
        try:
            # Simple cognitive complexity calculation
            cognitive_score = 0
            
            # Nested control structures
            nesting_level = 0
            for line in code.split('\n'):
                line = line.strip()
                
                # Increase nesting level for control structures
                if re.search(r'\b(if|for|while|match)\b.*{$', line):
                    cognitive_score += nesting_level + 1
                    nesting_level += 1
                
                # Decrease nesting level for closing braces
                elif line == '}':
                    nesting_level = max(0, nesting_level - 1)
                
                # Add score for logical operators
                cognitive_score += line.count('&&') + line.count('||')
            
            return cognitive_score
            
        except Exception as e:
            logger.error(f"Error calculating cognitive complexity: {str(e)}")
            return 0

    async def _calculate_inheritance_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate inheritance-related metrics."""
        try:
            # Find contract definitions and their inheritance
            contracts = re.finditer(
                r'contract\s+(\w+)(?:\s+is\s+([^{]+)){0,1}',
                code
            )
            
            inheritance_data = []
            max_depth = 0
            
            for contract in contracts:
                name = contract.group(1)
                parents = (
                    [p.strip() for p in contract.group(2).split(',')]
                    if contract.group(2)
                    else []
                )
                
                # Calculate inheritance depth
                depth = 1 + max(
                    (self._get_inheritance_depth(p, code) for p in parents),
                    default=0
                )
                max_depth = max(max_depth, depth)
                
                inheritance_data.append({
                    "contract": name,
                    "parents": parents,
                    "depth": depth
                })
            
            return {
                "inheritance": {
                    "max_depth": max_depth,
                    "contracts": inheritance_data
                }
            }
        except Exception as e:
            logger.error(f"Error calculating inheritance metrics: {str(e)}")
            return {"inheritance": {}}

    def _get_inheritance_depth(self, contract_name: str, code: str) -> int:
        """Recursively calculate inheritance depth for a contract."""
        try:
            # Find contract definition
            match = re.search(
                rf'contract\s+{contract_name}(?:\s+is\s+([^{{]+)){0,1}',
                code
            )
            
            if not match:
                return 0
                
            # Get parent contracts
            parents = (
                [p.strip() for p in match.group(1).split(',')]
                if match.group(1)
                else []
            )
            
            # Recursively get max depth of parents
            return 1 + max(
                (self._get_inheritance_depth(p, code) for p in parents),
                default=0
            )
            
        except Exception as e:
            logger.error(f"Error calculating inheritance depth: {str(e)}")
            return 0

    async def _calculate_function_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate function-related metrics."""
        try:
            # Find all function definitions
            functions = re.finditer(
                r'function\s+(\w+)\s*\(([^)]*)\)',
                code
            )
            
            function_data = []
            total_params = 0
            visibility_counts = {
                "public": 0,
                "private": 0,
                "internal": 0,
                "external": 0
            }
            
            for func in functions:
                name = func.group(1)
                params = [p.strip() for p in func.group(2).split(',') if p.strip()]
                
                # Determine visibility
                visibility = "public"  # default
                for v in visibility_counts.keys():
                    if re.search(rf'\b{v}\b', func.group(0)):
                        visibility = v
                        break
                
                visibility_counts[visibility] += 1
                total_params += len(params)
                
                function_data.append({
                    "name": name,
                    "params": len(params),
                    "visibility": visibility
                })
            
            return {
                "functions": {
                    "total": len(function_data),
                    "avg_params": round(total_params / len(function_data), 2) if function_data else 0,
                    "visibility": visibility_counts,
                    "details": function_data
                }
            }
        except Exception as e:
            logger.error(f"Error calculating function metrics: {str(e)}")
            return {"functions": {}}

    async def _calculate_variable_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate variable-related metrics."""
        try:
            # Find state variables
            state_vars = re.finditer(
                r'(public|private|internal)?\s*([\w\[\]]+)\s+(\w+)\s*;',
                code
            )
            
            variable_data = []
            type_counts = {}
            visibility_counts = {
                "public": 0,
                "private": 0,
                "internal": 0
            }
            
            for var in state_vars:
                visibility = var.group(1) or "internal"  # default
                var_type = var.group(2)
                name = var.group(3)
                
                visibility_counts[visibility] += 1
                type_counts[var_type] = type_counts.get(var_type, 0) + 1
                
                variable_data.append({
                    "name": name,
                    "type": var_type,
                    "visibility": visibility
                })
            
            return {
                "variables": {
                    "total": len(variable_data),
                    "by_type": type_counts,
                    "visibility": visibility_counts,
                    "details": variable_data
                }
            }
        except Exception as e:
            logger.error(f"Error calculating variable metrics: {str(e)}")
            return {"variables": {}}

    async def _calculate_dependency_metrics(self, code: str) -> Dict[str, Any]:
        """Calculate dependency-related metrics."""
        try:
            # Find import statements and contract dependencies
            imports = re.finditer(r'import\s+["\']([^"\']+)["\'];', code)
            dependencies = set()
            
            for imp in imports:
                dependencies.add(imp.group(1))
            
            # Find interface dependencies
            interfaces = re.finditer(r'interface\s+(\w+)', code)
            interface_deps = set(i.group(1) for i in interfaces)
            
            # Find library dependencies
            libraries = re.finditer(r'using\s+(\w+)', code)
            library_deps = set(l.group(1) for l in libraries)
            
            return {
                "dependencies": {
                    "total": len(dependencies) + len(interface_deps) + len(library_deps),
                    "imports": list(dependencies),
                    "interfaces": list(interface_deps),
                    "libraries": list(library_deps)
                }
            }
        except Exception as e:
            logger.error(f"Error calculating dependency metrics: {str(e)}")
            return {"dependencies": {}}
