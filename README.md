# Solana Multi-Agent System

A distributed multi-agent system for Web3 development and Solana analytics, featuring AI-powered development assistance, real-time analytics, and Discord integration.

## Features

- Web3 Development Agent: AI-powered Solana development assistance
- Analytics Agent: Real-time price tracking and sentiment analysis
- Discord Bot: Interactive interface for accessing agent services
- FastAPI Gateway: RESTful API for system interaction
- Scalable Architecture: Built with Docker and ready for cloud deployment

## Tech Stack

- **Backend**: Python, FastAPI, Celery
- **Database**: PostgreSQL
- **Message Broker**: RabbitMQ
- **AI/ML**: LLM integration (OpenAI/Anthropic/DeepSeek)
- **Deployment**: Docker, Docker Compose

## Getting Started

1. Clone the repository
2. Copy `.env.example` to `.env` and fill in your credentials
3. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

## Environment Variables

Create a `.env` file with the following variables:

```
# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here  # Optional
DEEPSEEK_ENDPOINT=your_endpoint  # Optional

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Message Broker
BROKER_URL=amqp://user:pass@rabbitmq:5672/

# Discord
DISCORD_TOKEN=your_token_here

# Analytics
TWITTER_BEARER_TOKEN=your_token_here
```

## Project Structure

```
/
├── README.md                     # Project documentation
├── docker-compose.yml           # Service orchestration
├── .env.example                 # Environment variables template
├── api_gateway/                 # FastAPI service
├── agents/                      # AI agents
├── discord_bot/                # Discord bot
├── frontend/                   # Optional web dashboard
├── scripts/                    # Utility scripts
└── tests/                     # Test suite
```

## Development

To start development:

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start services:
   ```bash
   docker-compose up -d rabbitmq postgres
   ```

3. Run the API:
   ```bash
   uvicorn api_gateway.main:app --reload
   ```

4. Run Celery workers:
   ```bash
   celery -A agents.tasks worker --loglevel=info
   ```

## Testing

Run tests with:
```bash
pytest
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License
