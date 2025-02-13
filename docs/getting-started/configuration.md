# Configuration

{% hint style="info" %}
Learn how to configure Sand Framework for your specific needs.
{% endhint %}

## Environment Variables

### Core Configuration
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
ENVIRONMENT=production  # development, staging, production

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
DATABASE_POOL_SIZE=20

# Message Broker
BROKER_URL=amqp://user:pass@rabbitmq:5672/
BROKER_POOL_LIMIT=10
```

### AI Service Configuration
```bash
# LLM Provider Settings
LLM_PROVIDER=openai  # openai, anthropic, or deepseek
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4  # or gpt-3.5-turbo
ANTHROPIC_API_KEY=your_key_here  # Optional
DEEPSEEK_ENDPOINT=your_endpoint  # Optional
```

### Analytics Configuration
```bash
# Social Media Integration
TWITTER_BEARER_TOKEN=your_token_here
TWITTER_QUERY_INTERVAL=300  # seconds

# Price Tracking
PRICE_UPDATE_INTERVAL=5  # seconds
PRICE_ALERT_WEBHOOK=your_webhook_url
```

## Feature Flags

Configure features in `config.yaml`:

```yaml
features:
  ai_copilot: true
  contract_analysis: true
  analytics: true
  discord_bot: true
  
security:
  rate_limiting: true
  jwt_auth: true
  
scaling:
  max_workers: 4
  cache_size: 1000
```

## Logging Configuration

{% tabs %}
{% tab title="Development" %}
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```
{% endtab %}

{% tab title="Production" %}
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'sand.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,
            'level': 'INFO',
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'INFO',
    },
}
```
{% endtab %}
{% endtabs %}

## Cache Configuration

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

{% hint style="warning" %}
Always use secure, unique passwords in production and never commit sensitive credentials to version control.
{% endhint %}
