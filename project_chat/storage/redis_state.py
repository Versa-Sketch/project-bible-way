"""
Redis-backed helpers for WebSocket-related state.

This module centralizes all Redis usage for real-time features so that
consumers and utilities do not rely on in-memory module-level globals.
"""

import os
import time
from datetime import datetime, timezone
from typing import Dict, Tuple, Optional

import redis


_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> redis.Redis:
    """
    Get a singleton Redis client using REDIS_URL.

    Uses a URL so it works both locally and in production (e.g. Docker, cloud).
    """
    global _redis_client
    if _redis_client is None:
        redis_url = os.getenv("REDIS_URL", "redis://127.0.0.1:6379/0")
        _redis_client = redis.Redis.from_url(redis_url)
    return _redis_client


# ---------------------------------------------------------------------------
# Presence helpers
# ---------------------------------------------------------------------------

ONLINE_USERS_KEY = "ws:online_users"


def mark_user_online(user_id: str) -> datetime:
    """
    Mark a user as online and record the last_seen timestamp.

    Returns the datetime used for last_seen (UTC).
    """
    client = get_redis_client()
    now = datetime.now(timezone.utc)
    client.hset(ONLINE_USERS_KEY, user_id, now.isoformat())
    return now


def mark_user_offline(user_id: str) -> None:
    """Mark a user as offline by removing them from the online_users hash."""
    client = get_redis_client()
    client.hdel(ONLINE_USERS_KEY, user_id)


def get_last_seen(user_id: str) -> Optional[datetime]:
    """
    Get the last_seen datetime for a user if present.
    """
    client = get_redis_client()
    value = client.hget(ONLINE_USERS_KEY, user_id)
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.decode())
    except Exception:
        return None


def is_user_online(user_id: str) -> bool:
    """Return True if the user is currently marked as online."""
    client = get_redis_client()
    return bool(client.hexists(ONLINE_USERS_KEY, user_id))


def get_all_online_users() -> Dict[str, datetime]:
    """
    Return a mapping of user_id -> last_seen (as datetime) for all online users.
    """
    client = get_redis_client()
    raw = client.hgetall(ONLINE_USERS_KEY)
    result: Dict[str, datetime] = {}
    for key, value in raw.items():
        user_id = key.decode()
        try:
            result[user_id] = datetime.fromisoformat(value.decode())
        except Exception:
            # If parsing fails, skip that entry instead of breaking everything.
            continue
    return result


# ---------------------------------------------------------------------------
# Rate limiting helpers
# ---------------------------------------------------------------------------


def check_rate_limit_redis(
    user_id: str,
    action: str,
    max_requests: int = 30,
    window_seconds: int = 30,
) -> Tuple[bool, int]:
    """
    Redis-backed sliding-window rate limiter.

    Stores timestamps in a sorted set `ws:rate:<user_id>:<action>` and ensures
    only at most max_requests entries exist within the last window_seconds.
    """
    client = get_redis_client()
    key = f"ws:rate:{user_id}:{action}"
    now = int(time.time())
    window_start = now - window_seconds

    pipe = client.pipeline()
    # Drop old entries
    pipe.zremrangebyscore(key, 0, window_start)
    # Add current request with score = timestamp
    pipe.zadd(key, {str(now): now})
    # Count remaining entries
    pipe.zcard(key)
    # Ensure key expires after the window
    pipe.expire(key, window_seconds)
    _, _, count, _ = pipe.execute()

    if count > max_requests:
        return False, 0

    remaining = max_requests - count
    return True, remaining


