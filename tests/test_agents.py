import pytest
from agents.web3_agent import Web3DevAgent
from agents.analytics_agent import AnalyticsAgent
from agents.llm_client import LLMClient
from unittest.mock import patch, MagicMock

@pytest.fixture
def web3_agent():
    return Web3DevAgent()

@pytest.fixture
def analytics_agent():
    return AnalyticsAgent()

@pytest.mark.asyncio
async def test_web3_agent_answer_question(web3_agent):
    question = "How do I create a Solana program using Anchor?"
    with patch.object(LLMClient, 'generate_completion') as mock_generate:
        mock_generate.return_value = "First, install Anchor CLI..."
        answer = await web3_agent.answer_dev_question(question)
        assert answer is not None
        assert isinstance(answer, str)
        mock_generate.assert_called_once()

@pytest.mark.asyncio
async def test_web3_agent_create_project(web3_agent):
    with patch.object(LLMClient, 'generate_completion'):
        result = await web3_agent.create_project("test_project")
        assert result is not None
        assert isinstance(result, dict)
        assert "name" in result
        assert result["name"] == "test_project"

@pytest.mark.asyncio
async def test_analytics_agent_get_price(analytics_agent):
    with patch('requests.get') as mock_get:
        mock_get.return_value.json.return_value = {
            "solana": {"usd": 100.0}
        }
        mock_get.return_value.status_code = 200
        
        result = await analytics_agent.get_current_price()
        assert result is not None
        assert isinstance(result, dict)
        assert "price_usd" in result
        assert result["price_usd"] == 100.0

@pytest.mark.asyncio
async def test_analytics_agent_get_sentiment(analytics_agent):
    with patch.object(analytics_agent, '_fetch_recent_tweets') as mock_fetch:
        mock_fetch.return_value = [
            {"text": "Solana is amazing!"},
            {"text": "Not happy with Solana today"}
        ]
        
        result = await analytics_agent.get_current_sentiment()
        assert result is not None
        assert isinstance(result, dict)
        assert "sentiment_score" in result
        assert isinstance(result["sentiment_score"], float)

@pytest.mark.asyncio
async def test_analytics_agent_generate_alerts(analytics_agent):
    with patch.object(analytics_agent, 'get_current_price') as mock_price:
        with patch.object(analytics_agent, 'get_current_sentiment') as mock_sentiment:
            mock_price.return_value = {"price_usd": 100.0}
            mock_sentiment.return_value = {"sentiment_score": 0.8}
            
            alerts = await analytics_agent.generate_alerts()
            assert isinstance(alerts, list)
