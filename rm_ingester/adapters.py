from datetime import datetime

import redis


class RedisSetStore:
    def __init__(self, client: redis.Redis, namespace: str):
        self._redis = client
        self._namespace = namespace

    def __contains__(self, item):
        return self._redis.hexists(self._namespace, str(item))

    def add(self, item):
        timestamp = datetime.now().isoformat()
        self._redis.hset(self._namespace, str(item), timestamp)
