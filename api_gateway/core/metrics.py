from prometheus_client import Counter, Histogram, Gauge
import time

# Request metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency in seconds',
    ['method', 'endpoint']
)

# Agent metrics
AGENT_TASK_COUNT = Counter(
    'agent_tasks_total',
    'Total number of agent tasks',
    ['agent_type', 'task_type', 'status']
)

AGENT_TASK_DURATION = Histogram(
    'agent_task_duration_seconds',
    'Agent task duration in seconds',
    ['agent_type', 'task_type']
)

# System metrics
SYSTEM_MEMORY_USAGE = Gauge(
    'system_memory_usage_bytes',
    'Current system memory usage in bytes'
)

SYSTEM_CPU_USAGE = Gauge(
    'system_cpu_usage_percent',
    'Current system CPU usage percentage'
)

# Database metrics
DB_CONNECTION_POOL_SIZE = Gauge(
    'db_connection_pool_size',
    'Current database connection pool size'
)

DB_QUERY_DURATION = Histogram(
    'db_query_duration_seconds',
    'Database query duration in seconds',
    ['query_type']
)

# Cache metrics
CACHE_HIT_COUNT = Counter(
    'cache_hits_total',
    'Total number of cache hits',
    ['cache_type']
)

CACHE_MISS_COUNT = Counter(
    'cache_misses_total',
    'Total number of cache misses',
    ['cache_type']
)

# Custom metrics for our agents
SOLANA_PRICE = Gauge(
    'solana_price_usd',
    'Current Solana price in USD'
)

SENTIMENT_SCORE = Gauge(
    'solana_sentiment_score',
    'Current Solana sentiment score',
    ['source']
)

def track_request_duration(method, endpoint):
    """Context manager to track request duration."""
    start_time = time.time()
    
    def stop_timer(response_status):
        duration = time.time() - start_time
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response_status).inc()
        REQUEST_LATENCY.labels(method=method, endpoint=endpoint).observe(duration)
    
    return stop_timer

def track_agent_task(agent_type, task_type):
    """Context manager to track agent task execution."""
    start_time = time.time()
    
    def stop_timer(status="success"):
        duration = time.time() - start_time
        AGENT_TASK_COUNT.labels(
            agent_type=agent_type,
            task_type=task_type,
            status=status
        ).inc()
        AGENT_TASK_DURATION.labels(
            agent_type=agent_type,
            task_type=task_type
        ).observe(duration)
    
    return stop_timer

def update_system_metrics(memory_usage, cpu_usage):
    """Update system resource metrics."""
    SYSTEM_MEMORY_USAGE.set(memory_usage)
    SYSTEM_CPU_USAGE.set(cpu_usage)

def track_db_query(query_type):
    """Context manager to track database query duration."""
    start_time = time.time()
    
    def stop_timer():
        duration = time.time() - start_time
        DB_QUERY_DURATION.labels(query_type=query_type).observe(duration)
    
    return stop_timer

def record_cache_result(cache_type, hit):
    """Record cache hit/miss."""
    if hit:
        CACHE_HIT_COUNT.labels(cache_type=cache_type).inc()
    else:
        CACHE_MISS_COUNT.labels(cache_type=cache_type).inc()

def update_solana_metrics(price, sentiment_score, source="twitter"):
    """Update Solana-specific metrics."""
    SOLANA_PRICE.set(price)
    SENTIMENT_SCORE.labels(source=source).set(sentiment_score)
