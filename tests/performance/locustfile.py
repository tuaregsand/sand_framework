from locust import HttpUser, task, between
import json

class ContractAnalysisUser(HttpUser):
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Load test data on startup."""
        with open("tests/fixtures/contracts/sample.sol", "r") as f:
            self.sample_contract = f.read()
    
    @task(3)  # Higher weight for this common operation
    def analyze_contract(self):
        """Test contract analysis endpoint."""
        response = self.client.post(
            "/api/v1/analyze",
            json={"content": self.sample_contract}
        )
        
        if response.status_code != 200:
            response.failure(f"Analysis failed with status {response.status_code}")
    
    @task(2)
    def get_security_issues(self):
        """Test security analysis endpoint."""
        response = self.client.post(
            "/api/v1/analyze/security",
            json={"content": self.sample_contract}
        )
        
        if response.status_code != 200:
            response.failure(f"Security analysis failed with status {response.status_code}")
    
    @task(2)
    def get_gas_optimizations(self):
        """Test gas optimization endpoint."""
        response = self.client.post(
            "/api/v1/analyze/gas",
            json={"content": self.sample_contract}
        )
        
        if response.status_code != 200:
            response.failure(f"Gas analysis failed with status {response.status_code}")
    
    @task(1)
    def get_code_quality(self):
        """Test code quality endpoint."""
        response = self.client.post(
            "/api/v1/analyze/quality",
            json={"content": self.sample_contract}
        )
        
        if response.status_code != 200:
            response.failure(f"Quality analysis failed with status {response.status_code}")
    
    @task(1)
    def get_metrics(self):
        """Test metrics endpoint."""
        response = self.client.post(
            "/api/v1/analyze/metrics",
            json={"content": self.sample_contract}
        )
        
        if response.status_code != 200:
            response.failure(f"Metrics analysis failed with status {response.status_code}")

class LargeContractUser(HttpUser):
    wait_time = between(3, 5)  # Longer wait times for large contracts
    
    def on_start(self):
        """Load large test contract."""
        with open("tests/fixtures/contracts/large_sample.sol", "r") as f:
            self.large_contract = f.read()
    
    @task
    def analyze_large_contract(self):
        """Test analysis of large contracts."""
        response = self.client.post(
            "/api/v1/analyze",
            json={"content": self.large_contract}
        )
        
        if response.status_code != 200:
            response.failure(f"Large contract analysis failed with status {response.status_code}")

class ConcurrentUser(HttpUser):
    wait_time = between(0.1, 0.5)  # Very short wait times to test concurrency
    
    def on_start(self):
        """Load multiple test contracts."""
        self.contracts = []
        for i in range(5):
            with open(f"tests/fixtures/contracts/contract_{i}.sol", "r") as f:
                self.contracts.append(f.read())
    
    @task
    def analyze_multiple_contracts(self):
        """Test concurrent analysis of multiple contracts."""
        for contract in self.contracts:
            self.client.post(
                "/api/v1/analyze",
                json={"content": contract},
                name="/api/v1/analyze (concurrent)"
            )

# To run:
# locust -f tests/performance/locustfile.py --host=http://localhost:8000
