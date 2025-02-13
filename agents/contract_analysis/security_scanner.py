import re
import ast
from typing import List, Dict, Any
import logging
from pathlib import Path
import json
import asyncio

logger = logging.getLogger(__name__)

class SecurityScanner:
    """Scanner for identifying security vulnerabilities in smart contracts."""
    
    def __init__(self):
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.custom_rules = self._load_custom_rules()
        self.code = None

    def _load_vulnerability_patterns(self) -> Dict[str, Any]:
        """Load vulnerability patterns from JSON file."""
        try:
            patterns_path = Path(__file__).parent / "data" / "vulnerability_patterns.json"
            with open(patterns_path) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading vulnerability patterns: {str(e)}")
            return {}

    def _load_custom_rules(self) -> List[Dict[str, Any]]:
        """Load custom security rules."""
        try:
            rules_path = Path(__file__).parent / "data" / "security_rules.json"
            with open(rules_path) as f:
                data = json.load(f)
                return data.get("rules", [])
        except Exception as e:
            logger.error(f"Error loading custom rules: {str(e)}")
            return []

    async def scan(self, code: str) -> List[Dict[str, Any]]:
        """
        Scan contract code for security vulnerabilities.
        
        Args:
            code: Smart contract source code
            
        Returns:
            List of security issues found, each containing:
            - id: Unique identifier for the vulnerability
            - name: Name of the vulnerability
            - description: Detailed description of the issue
            - severity: Severity level (critical, high, medium, low, info)
            - line_number: Line number where the issue was found
            - snippet: Code snippet containing the vulnerability
        """
        self.code = code
        issues = []

        # For now, use simple pattern matching since we're dealing with mixed syntax
        lines = code.split('\n')
        
        # Track which lines we've already reported issues for
        reported_lines = set()
        
        # Track function context
        current_function_start = None
        current_function_end = None
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):  # Skip empty lines and comments
                continue

            # Track function boundaries
            if 'def ' in line or 'fn ' in line:
                current_function_start = i
                # Find function end by looking for next non-indented line
                for j, next_line in enumerate(lines[i:], i + 1):
                    if next_line.strip() and not next_line.startswith(' '):
                        current_function_end = j - 1
                        break
                if not current_function_end:
                    current_function_end = len(lines)

            # Check for reentrancy (external call followed by state change)
            if any(pattern in line for pattern in ['invoke_signed', 'invoke', 'transfer', 'send', 'call']):
                # Only look for state changes within the same function
                if current_function_start and current_function_end:
                    for j in range(i + 1, current_function_end + 1):
                        if j >= len(lines):
                            break
                        next_line = lines[j].strip()
                        if any(pattern in next_line for pattern in ['balance', 'withdraw', 'transfer', '=', '-=']):
                            if i not in reported_lines:  # Only report once per line
                                issues.append({
                                    'id': 'REENTRANCY',
                                    'name': 'Reentrancy Vulnerability',
                                    'description': 'External call is made before state changes, potentially allowing reentrancy attacks',
                                    'severity': 'critical',
                                    'line_number': i,
                                    'snippet': line
                                })
                                reported_lines.add(i)
                            break

            # Check for missing access control
            if ('pub fn' in line or 'def' in line) and ('admin' in line or 'withdraw' in line or 'transfer' in line):
                # Look for access control decorators or checks in function body
                function_lines = lines[i-1:current_function_end] if current_function_end else lines[i-1:]
                if not any('requires_auth' in l or 'admin_only' in l or 'authority' in l for l in function_lines):
                    if i not in reported_lines:
                        issues.append({
                            'id': 'NO_ACCESS_CONTROL',
                            'name': 'Missing Access Control',
                            'description': 'Public function with admin capabilities lacks access control',
                            'severity': 'high',
                            'line_number': i,
                            'snippet': line
                        })
                        reported_lines.add(i)

            # Check for missing input validation
            if ('fn' in line or 'def' in line) and '(' in line and ')' in line:
                params = line[line.index('(')+1:line.index(')')].strip()
                if params:
                    # Look for validation in function body
                    function_lines = lines[i:current_function_end] if current_function_end else lines[i:]
                    if not any('assert' in l or 'require' in l or 'validate' in l or 'check' in l for l in function_lines):
                        if i not in reported_lines:
                            issues.append({
                                'id': 'NO_INPUT_VALIDATION',
                                'name': 'Missing Input Validation',
                                'description': 'Function parameters lack input validation',
                                'severity': 'medium',
                                'line_number': i,
                                'snippet': line
                            })
                            reported_lines.add(i)

            # Check for PDA validation
            if 'find_program_address' in line:
                # Look for validation in next few lines
                validation_range = min(i + 5, len(lines)) if current_function_end is None else min(current_function_end, i + 5)
                if not any('verify_program_address' in lines[j] or 'check_program_address' in lines[j] for j in range(i, validation_range)):
                    if i not in reported_lines:
                        issues.append({
                            'id': 'INVALID_PDA',
                            'name': 'Invalid PDA Validation',
                            'description': 'PDA creation lacks proper validation',
                            'severity': 'high',
                            'line_number': i,
                            'snippet': line
                        })
                        reported_lines.add(i)

            # Check for arithmetic operations
            if any(op in line for op in ['+', '-', '*', '/']):
                # Look for safety checks in surrounding context
                context_start = max(0, i - 3)
                context_end = min(len(lines), i + 3)
                if not any('checked_' in lines[j] or 'safe_' in lines[j] or 'overflow' in lines[j] for j in range(context_start, context_end)):
                    if i not in reported_lines:
                        issues.append({
                            'id': 'UNCHECKED_ARITHMETIC',
                            'name': 'Unchecked Arithmetic Operation',
                            'description': 'Arithmetic operation without overflow/underflow checks',
                            'severity': 'medium',
                            'line_number': i,
                            'snippet': line
                        })
                        reported_lines.add(i)

        return issues

    async def _check_reentrancy(self, tree: ast.AST, issues: List[Dict[str, Any]]) -> None:
        """Check for reentrancy vulnerabilities."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                external_calls = []
                state_changes = []
                
                # First pass: collect all external calls and state changes
                for child in ast.walk(node):
                    if isinstance(child, ast.Call) and self._is_external_call(child):
                        external_calls.append(child)
                    elif self._is_state_change(child):
                        state_changes.append(child)
                
                # Second pass: check if any external call is followed by a state change
                for ext_call in external_calls:
                    for state_change in state_changes:
                        if hasattr(state_change, 'lineno') and hasattr(ext_call, 'lineno'):
                            if state_change.lineno > ext_call.lineno:
                                issues.append({
                                    'id': 'REENTRANCY',
                                    'name': 'Reentrancy Vulnerability',
                                    'description': 'External call is made before state changes, potentially allowing reentrancy attacks',
                                    'severity': 'critical',
                                    'line_number': ext_call.lineno,
                                    'snippet': ast.get_source_segment(self.code, ext_call)
                                })
                                break

    def _is_state_change(self, node: ast.AST) -> bool:
        """Check if a node represents a state change."""
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            return True
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                state_change_patterns = [
                    'balance',
                    'withdraw',
                    'transfer',
                    'mint',
                    'burn',
                    'set_',
                    'update_'
                ]
                return any(pattern in node.func.attr for pattern in state_change_patterns)
        return False

    def _is_external_call(self, node: ast.Call) -> bool:
        """Check if a call is to an external contract."""
        if isinstance(node.func, ast.Attribute):
            # Check for common external call patterns
            external_patterns = [
                'invoke_signed',
                'invoke',
                'transfer',
                'send',
                'call',
                'delegatecall'
            ]
            return any(pattern in node.func.attr for pattern in external_patterns)
        return False

    async def _check_access_control(self, tree: ast.AST, issues: List[Dict[str, Any]]) -> None:
        """Check for access control vulnerabilities."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Look for pub fn or sensitive operations without access control
                is_public = False
                has_sensitive_ops = False
                
                # Check if function is public
                for decorator in ast.walk(node):
                    if isinstance(decorator, ast.Name) and decorator.id == 'pub':
                        is_public = True
                        break
                
                # Check for sensitive operations
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            sensitive_patterns = ['withdraw', 'transfer', 'admin', 'owner']
                            if any(pattern in child.func.attr for pattern in sensitive_patterns):
                                has_sensitive_ops = True
                                break
                
                if (is_public or has_sensitive_ops) and not self._has_access_control(node):
                    issues.append({
                        'id': 'NO_ACCESS_CONTROL',
                        'name': 'Missing Access Control',
                        'description': f'Function {node.name} lacks proper access control',
                        'severity': 'high',
                        'line_number': node.lineno,
                        'snippet': ast.get_source_segment(self.code, node)
                    })

    def _has_access_control(self, node: ast.FunctionDef) -> bool:
        """Check if a function has proper access control."""
        # Look for decorators or checks that implement access control
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in ['requires_auth', 'admin_only']:
                    return True
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id in ['requires_auth', 'admin_only']:
                        return True
        
        # Check function body for authority checks
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if 'authority' in child.func.attr:
                        return True
        return False

    def _has_input_validation(self, node: ast.arg) -> bool:
        """Check if a parameter has input validation."""
        # Look for parent function
        current_function = None
        for parent in ast.walk(node):
            if isinstance(parent, ast.FunctionDef):
                current_function = parent
                break
                
        if current_function:
            # Look for validation patterns in function body
            for child in ast.walk(current_function):
                if isinstance(child, ast.Assert):
                    # Check if assertion involves our parameter
                    for name_node in ast.walk(child.test):
                        if isinstance(name_node, ast.Name) and name_node.id == node.arg:
                            return True
                elif isinstance(child, ast.Call):
                    # Check for require/check/validate calls
                    if isinstance(child.func, ast.Name):
                        if child.func.id in ['require', 'check', 'validate']:
                            for arg in child.args:
                                for name_node in ast.walk(arg):
                                    if isinstance(name_node, ast.Name) and name_node.id == node.arg:
                                        return True
        return False

    async def _check_input_validation(self, tree: ast.AST, issues: List[Dict[str, Any]]) -> None:
        """Check for input validation vulnerabilities."""
        for node in ast.walk(tree):
            if isinstance(node, ast.arg):
                if not self._has_input_validation(node):
                    issues.append({
                        'id': 'NO_INPUT_VALIDATION',
                        'name': 'Missing Input Validation',
                        'description': f'Parameter {node.arg} lacks input validation',
                        'severity': 'medium',
                        'line_number': node.lineno,
                        'snippet': ast.get_source_segment(self.code, node)
                    })

    def _is_pda_creation(self, node: ast.Call) -> bool:
        """Check if a call creates a PDA."""
        if isinstance(node.func, ast.Attribute):
            pda_patterns = [
                'create_program_address',
                'find_program_address',
                'try_find_program_address'
            ]
            return any(pattern in node.func.attr for pattern in pda_patterns)
        return False

    def _has_pda_validation(self, node: ast.Call) -> bool:
        """Check if PDA creation includes proper validation."""
        # Look for validation after PDA creation
        current_block = None
        for parent in ast.walk(node):
            if isinstance(parent, (ast.FunctionDef, ast.If, ast.With)):
                current_block = parent
                break
                
        if current_block:
            validation_found = False
            for child in ast.walk(current_block):
                if isinstance(child, ast.Call):
                    if isinstance(child.func, ast.Attribute):
                        # Check for common PDA validation patterns
                        validation_patterns = [
                            'verify_program_address',
                            'check_program_address',
                            'validate_pda',
                            'assert_pda_matches',
                            'verify_derivation'
                        ]
                        if any(pattern in child.func.attr for pattern in validation_patterns):
                            validation_found = True
                            break
            return validation_found
        return False

    async def _check_pda_validation(self, tree: ast.AST, issues: List[Dict[str, Any]]) -> None:
        """Check for PDA validation vulnerabilities."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and self._is_pda_creation(node):
                if not self._has_pda_validation(node):
                    issues.append({
                        'id': 'INVALID_PDA',
                        'name': 'Invalid PDA Validation',
                        'description': 'PDA creation lacks proper validation',
                        'severity': 'high',
                        'line_number': node.lineno,
                        'snippet': ast.get_source_segment(self.code, node)
                    })

    async def _check_arithmetic(self, tree: ast.AST, issues: List[Dict[str, Any]]) -> None:
        """Check for unchecked arithmetic operations."""
        for node in ast.walk(tree):
            if isinstance(node, (ast.BinOp, ast.AugAssign)):
                # Check for arithmetic operations without overflow checks
                if isinstance(node.op, (ast.Add, ast.Sub, ast.Mult)):
                    issues.append({
                        'id': 'UNCHECKED_ARITHMETIC',
                        'name': 'Unchecked Arithmetic Operation',
                        'description': 'Arithmetic operation without overflow/underflow checks',
                        'severity': 'medium',
                        'line_number': node.lineno,
                        'snippet': ast.get_source_segment(self.code, node)
                    })
