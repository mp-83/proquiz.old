import os

from redis import Redis

rclient = Redis(**{"host": "redis", "port": "6379", "password": os.getenv("REDIS_PW")})
