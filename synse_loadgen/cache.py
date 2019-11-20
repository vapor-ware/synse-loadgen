"""Async-safe in-memory cache for Synse LoadGen."""

import asyncio
from typing import Any


class AsyncCache:
    """A simple async-safe cache with a dictionary backing."""

    def __init__(self) -> None:
        self.lock = asyncio.Lock()
        self.state = {}

    async def clear(self) -> None:
        async with self.lock:
            self.state = {}

    async def set(self, key: str, val: Any) -> None:
        async with self.lock:
            self.state[key] = val

    async def get(self, key: str) -> Any:
        async with self.lock:
            return self.state.get(key)
