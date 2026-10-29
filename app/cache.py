"""Redis-backed TTL cache for YahooLeague methods. Yahoo's API is slow and rate limited,
so cache everything. Keys include the user and league, so users never see each other's data.
If Redis hiccups, we fall through to a live Yahoo call instead of failing the request."""
import hashlib
import json
import logging
from functools import wraps

import redis

from .redis_client import r

log = logging.getLogger(__name__)


def ttl_cache(seconds: int):
    def deco(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            args_hash = hashlib.sha1(
                json.dumps([args, kwargs], sort_keys=True, default=str).encode()
            ).hexdigest()[:16]
            key = f"cache:{self.guid}:{self.league_id}:{fn.__name__}:{args_hash}"
            try:
                hit = r.get(key)
                if hit is not None:
                    return json.loads(hit)
            except redis.RedisError:
                log.warning("cache read failed", exc_info=True)
            value = fn(self, *args, **kwargs)
            try:
                r.set(key, json.dumps(value, default=str), ex=seconds)
            except (redis.RedisError, TypeError):
                log.warning("cache write failed", exc_info=True)
            return value
        return wrapper
    return deco
