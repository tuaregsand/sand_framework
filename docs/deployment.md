# Deployment Guide

## Prerequisites
- Python 3.9+
- Redis
- PostgreSQL
- Docker (optional)

## Local Development Setup

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/sandframework.git
cd sandframework
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

4. **Environment Configuration**
Create a `.env` file in the project root:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/sandframework
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
MAX_WORKERS=4
RATE_LIMIT=100
```

5. **Database Setup**
```bash
alembic upgrade head
```

## Production Deployment

### Docker Deployment

1. **Build the Docker Image**
```bash
docker build -t sandframework .
```

2. **Run with Docker Compose**
```bash
docker-compose up -d
```

### Kubernetes Deployment

1. **Apply Kubernetes Configurations**
```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

2. **Verify Deployment**
```bash
kubectl get pods -n sandframework
```

### Monitoring Setup

1. **Prometheus Configuration**
```yaml
scrape_configs:
  - job_name: 'sandframework'
    static_configs:
      - targets: ['localhost:8000']
```

2. **Grafana Dashboard**
Import the provided dashboard from `monitoring/grafana/dashboard.json`

## Scaling Considerations

### Horizontal Scaling
- Use Kubernetes HPA (Horizontal Pod Autoscaling)
- Configure based on CPU/Memory metrics
```bash
kubectl autoscale deployment sandframework --cpu-percent=80 --min=3 --max=10
```

### Cache Configuration
- Adjust Redis cache size based on usage
- Implement cache eviction policies
- Monitor cache hit rates

### Database Optimization
- Index frequently queried fields
- Partition large tables
- Regular maintenance tasks

## Security Considerations

1. **API Security**
- Enable rate limiting
- Implement API key authentication
- Use HTTPS only

2. **Network Security**
- Configure firewalls
- Use private networks for internal services
- Implement network policies in Kubernetes

3. **Monitoring**
- Set up alerts for suspicious activities
- Monitor error rates and response times
- Regular security audits

## Backup and Recovery

1. **Database Backups**
```bash
# Automated daily backups
0 0 * * * pg_dump -U user -d sandframework > /backups/db_$(date +%Y%m%d).sql
```

2. **Application State**
- Regular snapshots of Redis state
- Backup of configuration files

## Troubleshooting

### Common Issues

1. **Performance Issues**
- Check Redis connection pool
- Monitor database query performance
- Review log files for bottlenecks

2. **Memory Problems**
- Adjust worker process count
- Monitor memory usage patterns
- Check for memory leaks

3. **Connection Issues**
- Verify network connectivity
- Check service dependencies
- Review firewall rules

### Logging

Configure logging in `logging.yaml`:
```yaml
version: 1
handlers:
  console:
    class: logging.StreamHandler
    level: INFO
  file:
    class: logging.FileHandler
    filename: /var/log/sandframework/app.log
    level: DEBUG
```

## Health Checks

Implement regular health checks:
```bash
curl http://localhost:8000/health
```

## Maintenance

1. **Regular Updates**
- Keep dependencies updated
- Apply security patches
- Update SSL certificates

2. **Performance Tuning**
- Regular database optimization
- Cache tuning
- Load testing

3. **Monitoring**
- Set up alerts
- Review metrics
- Analyze logs
