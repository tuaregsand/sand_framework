# Smart Contract Analysis API Documentation

## Overview
The Smart Contract Analysis system provides a comprehensive suite of tools for analyzing Solana smart contracts. The system includes security scanning, gas optimization, code quality checking, and metrics collection.

## Components

### SecurityScanner
```python
class SecurityScanner:
    async def scan(contract_content: str) -> List[Dict]
```
Performs security analysis of smart contracts, identifying potential vulnerabilities.

#### Returns
List of security issues, each containing:
- `severity`: Critical, High, Medium, or Low
- `title`: Brief description of the issue
- `description`: Detailed explanation
- `location`: File and line number
- `category`: Vulnerability category
- `recommendation`: How to fix
- `cwe_id`: Common Weakness Enumeration ID

### GasOptimizer
```python
class GasOptimizer:
    async def analyze(contract_content: str) -> List[Dict]
```
Analyzes contracts for gas optimization opportunities.

#### Returns
List of optimization suggestions, each containing:
- `title`: Optimization title
- `description`: What can be optimized
- `location`: Where in the code
- `potential_savings`: Estimated compute units saved
- `optimization_type`: Category of optimization
- `difficulty`: Easy, Medium, or Hard
- `recommendation`: How to implement

### CodeQualityChecker
```python
class CodeQualityChecker:
    async def check(contract_content: str) -> List[Dict]
```
Evaluates code quality and maintainability.

#### Returns
List of quality issues, each containing:
- `title`: Issue title
- `description`: Quality concern
- `location`: File and line number
- `severity`: High, Medium, or Low
- `category`: Quality category
- `recommendation`: How to improve
- `impact`: Effect on codebase

### ContractMetrics
```python
class ContractMetrics:
    async def calculate(contract_content: str) -> Dict
```
Collects comprehensive metrics about the contract.

#### Returns
Dictionary of metrics, each containing:
- `name`: Metric name
- `value`: Numerical value
- `category`: Metric category
- `description`: What it measures
- `threshold`: Reference value
- `status`: Current status

## Usage Example

```python
from agents.contract_analysis.analyzer import SmartContractAnalyzer

async def analyze_contract(contract_path: str):
    analyzer = SmartContractAnalyzer()
    with open(contract_path, 'r') as f:
        content = f.read()
    
    result = await analyzer.analyze(content)
    return result
```

## Error Handling
All components use async/await and proper error handling. Errors are logged and propagated appropriately.

## Rate Limits
- Maximum contract size: 1MB
- Maximum concurrent analyses: 10
- Rate limit: 100 requests per minute

## Best Practices
1. Always handle analysis results asynchronously
2. Cache results when possible
3. Implement proper error handling
4. Monitor memory usage for large contracts
