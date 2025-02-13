from locust import HttpUser, task, between
import json
import random

class SolanaAgentUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        """Set up test API key."""
        self.headers = {"X-API-Key": "test_api_key"}
    
    @task(3)
    def get_price(self):
        """Test price endpoint."""
        self.client.get(
            "/analytics/price",
            headers=self.headers
        )
    
    @task(2)
    def get_sentiment(self):
        """Test sentiment endpoint."""
        self.client.get(
            "/analytics/sentiment",
            headers=self.headers
        )
    
    @task(1)
    def ask_dev_question(self):
        """Test development question endpoint."""
        questions = [
            "How do I create a Solana program?",
            "What is the best way to handle errors in Anchor?",
            "How can I optimize gas fees?",
            "What are PDAs in Solana?",
            "How do I implement cross-program invocation?"
        ]
        
        self.client.post(
            "/dev/ask",
            json={"question": random.choice(questions)},
            headers=self.headers
        )
    
    @task(1)
    def create_project(self):
        """Test project creation endpoint."""
        project_name = f"test_project_{random.randint(1000, 9999)}"
        
        self.client.post(
            "/dev/project/new",
            json={
                "name": project_name,
                "description": "Test project for load testing",
                "framework": "anchor"
            },
            headers=self.headers
        )
    
    @task(4)
    def get_alerts(self):
        """Test alerts endpoint."""
        self.client.get(
            "/analytics/alerts",
            headers=self.headers
        )
    
    @task(2)
    def health_check(self):
        """Test health check endpoint."""
        self.client.get("/health")
