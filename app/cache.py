import time
import json

try:
    import redis
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
    redis_client.ping()
    USE_REDIS = True
except Exception:
    USE_REDIS = False
    _cache = {}

def get(key):
    if USE_REDIS:
        value = redis_client.get(key)
        if value is None:
            return None
        return json.loads(value)

    data = _cache.get(key)
    if not data:
        return None
    value, expiry = data
    if time.time() > expiry:
        del _cache[key]
        return None
    return value

def set(key, value, total=86400):
    if USE_REDIS:
        redis_client.setex(key, total, json.dumps(value))
        return

    _cache[key] = (value, time.time() + total)


def clear_cache():
    if USE_REDIS:
        redis_client.flushdb()
    else:
        _cache.clear()

