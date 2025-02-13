# Testing Guide

## Quick Start

### Prerequisites

1. **Python Environment**
   ```bash
   # Create and activate virtual environment
   python -m venv venv
   source venv/bin/activate

   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Redis Server** (Required for task queue)
   ```bash
   # Using Docker (recommended)
   docker run -d -p 6379:6379 --name sandframework-redis redis:alpine

   # Or install locally on Mac
   brew install redis
   brew services start redis
   ```

3. **Environment Setup**
   ```bash
   # Copy example env file
   cp .env.example .env.test

   # Update test database URL in .env.test:
   DATABASE_URL=postgresql://user:password@localhost:5432/sandframework_test
   REDIS_URL=redis://localhost:6379/0
   ```

### Running Tests

1. **Quick Test**
   ```bash
   # Run all tests with coverage
   python -m pytest tests/ -v --cov=api_gateway --cov=agents
   ```

2. **Run Specific Tests**
   ```bash
   # Run only API tests
   python -m pytest tests/api/

   # Run only metrics tests
   python -m pytest tests/api/test_metrics.py
   ```

3. **Test with Background Tasks**
   ```bash
   # Start Celery worker in a new terminal
   celery -A api_gateway.core.queue.celery_app worker --loglevel=info

   # Run tests in another terminal
   python -m pytest tests/
   ```

### Troubleshooting

1. **Database Issues**
   - Ensure PostgreSQL is running
   - Check database URL in .env.test
   - Run migrations: `alembic upgrade head`

2. **Redis Issues**
   - Check Redis is running: `redis-cli ping`
   - Verify Redis URL in .env.test
   - Clear Redis: `redis-cli flushall`

3. **Task Queue Issues**
   - Ensure Celery worker is running
   - Check Redis connection
   - View Celery logs for errors

## Overview

This guide covers the testing strategy and practices for the Smart Contract Analysis Framework. Our testing approach ensures high code quality and reliability through multiple testing layers.

## Test Structure

```
tests/
├── unit/                      # Unit tests
│   ├── test_security.py      # Security scanner tests
│   ├── test_gas.py          # Gas optimizer tests
│   ├── test_quality.py      # Code quality tests
│   └── test_metrics.py      # Metrics collector tests
├── integration/              # Integration tests
│   ├── test_analyzer.py     # Full analyzer pipeline
│   └── test_api.py         # API endpoint tests
├── performance/             # Performance tests
│   ├── test_large_contracts.py
│   └── locustfile.py       # Load testing
└── fixtures/               # Test data
    └── contracts/          # Sample contracts
```

## Running Tests

### Unit Tests
```bash
# Run all unit tests
pytest tests/unit

# Run specific test file
pytest tests/unit/test_security.py

# Run with coverage
pytest --cov=sandframework tests/unit
```

### Integration Tests
```bash
# Run all integration tests
pytest tests/integration

# Run with detailed output
pytest -v tests/integration
```

### Performance Tests
```bash
# Run performance tests
pytest tests/performance

# Run load tests with Locust
locust -f tests/performance/locustfile.py
```

## Test Categories

### 1. Unit Tests

#### Security Scanner Tests
- Vulnerability pattern detection
- False positive validation
- Edge case handling

#### Gas Optimizer Tests
- Optimization pattern recognition
- Savings calculations
- Recommendation accuracy

#### Code Quality Tests
- Style checking
- Complexity metrics
- Documentation coverage

#### Metrics Tests
- Metric calculations
- Threshold validation
- Data aggregation

### 2. Integration Tests

#### Analyzer Pipeline Tests
- End-to-end contract analysis
- Component interaction
- Error propagation

#### API Tests
- Endpoint functionality
- Request/response validation
- Authentication/authorization
- Rate limiting

### 3. Performance Tests

#### Large Contract Tests
- Memory usage
- Processing time
- Resource utilization

#### Load Tests
- Concurrent requests
- System stability
- Response times

## Test Data

### Sample Contracts
- Basic contracts
- Complex contracts
- Known vulnerability examples
- Optimization candidates

### Mock Data
- Security patterns
- Gas patterns
- Quality metrics
- Analysis results

## Best Practices

### Writing Tests

1. **Test Organization**
```python
def test_function_name():
    # Arrange
    input_data = ...
    
    # Act
    result = function_to_test(input_data)
    
    # Assert
    assert result == expected_output
```

2. **Use Fixtures**
```python
@pytest.fixture
def sample_contract():
    return load_contract("fixtures/contracts/sample.sol")

def test_analysis(sample_contract):
    result = analyze(sample_contract)
    assert result.issues == []
```

3. **Mock External Dependencies**
```python
@patch("agents.security_scanner.load_patterns")
def test_scanner(mock_load):
    mock_load.return_value = test_patterns
    scanner = SecurityScanner()
    result = scanner.scan(test_input)
```

### Test Coverage

- Maintain >90% code coverage
- Focus on critical paths
- Include edge cases
- Test error conditions

### Continuous Integration

- Tests run on every PR
- Coverage reports generated
- Performance benchmarks tracked
- Integration tests in staging

## Debugging Tests

### Common Issues

1. **Async Tests**
```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result
```

2. **Database Tests**
```python
def test_db_operation(test_db):
    # test_db is a fixture that provides a clean database
    result = perform_db_operation()
    assert result
```

### Useful Commands

```bash
# Run tests with print output
pytest -s

# Run tests with logging
pytest --log-cli-level=INFO

# Debug specific test
pytest tests/unit/test_file.py::test_function -vv

# Generate HTML coverage report
pytest --cov=sandframework --cov-report=html
```

## Performance Testing

### Load Testing with Locust

1. **Setup**
```python
from locust import HttpUser, task

class ContractAnalysisUser(HttpUser):
    @task
    def analyze_contract(self):
        self.client.post("/analyze", json={"content": "..."})
```

2. **Running**
```bash
locust -f tests/performance/locustfile.py
```

3. **Metrics to Monitor**
- Response time
- Error rate
- Throughput
- Resource usage

## Reporting

### Coverage Reports
- Generated after test runs
- Available in HTML format
- Tracked in CI/CD

### Test Results
- JUnit XML format
- Integrated with CI/CD
- Historical tracking

## Maintenance

### Regular Tasks
- Update test data
- Review coverage reports
- Update performance benchmarks
- Clean up test databases

### Documentation
- Keep test documentation updated
- Document new test patterns
- Maintain examples
- Update troubleshooting guides
