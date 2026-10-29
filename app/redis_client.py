import redis

from .config import settings

# Lazy connection: nothing is contacted until the first command.
r = redis.Redis.from_url(settings.redis_url, socket_timeout=5, socket_connect_timeout=5)
