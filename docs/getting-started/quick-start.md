# Quick Start

{% hint style="info" %}
Get up and running with Sand Framework in minutes!
{% endhint %}

## Prerequisites

* Docker and Docker Compose
* Node.js 16+ (for web frontend)
* Python 3.8+
* Solana CLI tools (optional)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd sandframework
```

2. Set up environment variables:
```bash
cp .env.example .env
```

3. Configure your `.env` file with required credentials:
```bash
# LLM Provider
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname

# Message Broker
BROKER_URL=amqp://user:pass@rabbitmq:5672/

# Discord (if using bot)
DISCORD_TOKEN=your_token_here
```

4. Start the services:
```bash
docker-compose up -d
```

{% hint style="success" %}
🎉 Congratulations! Sand Framework is now running locally.
{% endhint %}

## Verify Installation

1. Check API status:
```bash
curl http://localhost:8000/health
```

2. Access API documentation:
```bash
open http://localhost:8000/api/docs
```

3. Test Discord bot (if configured):
```bash
/sand health
```

## Next Steps

* [Configure your environment](configuration.md)
* [Explore the features](../features/ai-copilot.md)
* [Learn about the architecture](../development/architecture.md)
