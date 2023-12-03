import os
import redis

# Retrieve Redis connection settings from environment variables
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
redis_password = os.getenv('REDIS_PASSWORD', '')

# Redis connection
redis_conn = redis.Redis(
    host=redis_host,
    port=redis_port,
    password=redis_password
)
