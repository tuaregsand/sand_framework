# Sand Framework

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

# Sand Framework

A comprehensive smart contract analysis and development platform built for the Solana ecosystem. Sand Framework provides real-time security scanning, gas optimization, and collaborative development features through an intuitive infinite canvas interface.

## 🌟 Features

- **Smart Contract Analysis**
  - Real-time security vulnerability scanning
  - Gas optimization recommendations
  - Code quality metrics and best practices
  - Automated fix suggestions

- **Real-time Collaboration**
  - Infinite canvas interface for contract visualization
  - Multi-user real-time editing
  - Live comments and annotations
  - Project-based organization

- **Solana Integration**
  - Live contract monitoring
  - Real-time state updates
  - Transaction tracking
  - Performance metrics

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL
- Redis

### Installation

1. Clone the repository:
```bash
git clone https://github.com/tuaregsand/sand_framework.git
cd sand_framework
```

2. Set up the environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Initialize the database:
```bash
# Make sure PostgreSQL is running
python -m api_gateway.db init
```

5. Start the services:
```bash
# Start API Gateway
uvicorn api_gateway.main:app --reload

# Start Celery Worker
celery -A agents.tasks worker --loglevel=info
```

## 🏗️ Architecture

The Sand Framework consists of several microservices:

- **API Gateway**: FastAPI-based REST API
- **Analysis Workers**: Celery-based contract analysis engine
- **Monitoring Service**: Real-time Solana contract monitoring
- **Frontend**: Next.js-based infinite canvas interface

## 📚 API Documentation

API documentation is available at `/docs` when running the API Gateway. Key endpoints include:

- `/dev/analyze`: Submit contracts for analysis
- `/dev/projects`: Manage development projects
- `/metrics`: Get analysis metrics and results
- `/analytics`: Access real-time analytics

## 🧪 Testing

Run the test suite:
```bash
pytest tests/
```

For performance testing:
```bash
python -m tests.performance.locustfile
```

## 🔐 Security

- All API endpoints require authentication
- Real-time updates use secure WebSocket connections
- Sensitive data is encrypted at rest
- Regular security audits and updates

## 📈 Roadmap

- [ ] AI-powered code suggestions
- [ ] Cross-chain contract analysis
- [ ] Advanced visualization features
- [ ] Integration with popular IDEs

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Solana Foundation
- OpenZeppelin
- Trail of Bits

## 📞 Support

For support, please open an issue or contact the maintainers at support@sandframework.dev
