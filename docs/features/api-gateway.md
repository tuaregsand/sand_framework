# API Gateway

{% hint style="info" %}
The API Gateway provides RESTful endpoints to access all Sand Framework features.
{% endhint %}

## API Overview

Our FastAPI-based gateway provides:
* OpenAPI documentation
* Authentication & authorization
* Rate limiting
* Request validation
* Async operation support

## Authentication

{% tabs %}
{% tab title="JWT Auth" %}
```bash
# Get JWT token
curl -X POST http://localhost:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'

# Use token
curl -X GET http://localhost:8000/api/v1/analyze \
  -H "Authorization: Bearer <token>"
```
{% endtab %}

{% tab title="API Key" %}
```bash
# Use API key in header
curl -X GET http://localhost:8000/api/v1/analyze \
  -H "X-API-Key: your-api-key"
```
{% endtab %}
{% endtabs %}

## Endpoints

### AI Service
```
POST /api/v1/ai/analyze
POST /api/v1/ai/optimize
POST /api/v1/ai/explain
GET  /api/v1/ai/models
```

### Analytics
```
GET  /api/v1/analytics/price/{token}
GET  /api/v1/analytics/sentiment/{token}
POST /api/v1/analytics/alerts
GET  /api/v1/analytics/trends
```

### Contract Analysis
```
POST /api/v1/contracts/analyze
POST /api/v1/contracts/optimize
GET  /api/v1/contracts/{address}/audit
```

## Request Examples

### Analyze Contract
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/contracts/analyze",
    headers={"Authorization": f"Bearer {token}"},
    json={
        "code": contract_code,
        "settings": {
            "security_check": True,
            "optimization": True
        }
    }
)

results = response.json()
```

### Get Price Data
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/analytics/price/SOL",
    headers={"Authorization": f"Bearer {token}"}
)

price_data = response.json()
```

## Error Handling

{% tabs %}
{% tab title="HTTP Errors" %}
```json
{
  "status_code": 400,
  "message": "Invalid request parameters",
  "details": {
    "field": "code",
    "error": "Required field missing"
  }
}
```
{% endtab %}

{% tab title="Rate Limiting" %}
```json
{
  "status_code": 429,
  "message": "Too many requests",
  "retry_after": 60
}
```
{% endtab %}
{% endtabs %}

## WebSocket Support

For real-time updates:

```python
import websockets

async with websockets.connect(
    'ws://localhost:8000/ws/analytics'
) as websocket:
    await websocket.send(json.dumps({
        "subscribe": "price_updates",
        "symbols": ["SOL", "RAY"]
    }))
    
    while True:
        data = await websocket.recv()
        print(json.loads(data))
```

{% hint style="info" %}
Full API documentation is available at `/api/docs` when running the server.
{% endhint %}
