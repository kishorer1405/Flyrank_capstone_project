import threading
import time
from collections import defaultdict, deque


class RateLimiter:

    def __init__(
        self,
        limit: int,
        window_seconds: int = 60
    ):
        self.limit = limit
        self.window = window_seconds
        self._events = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> bool:
        now = time.monotonic()

        with self._lock:
            q = self._events[key]

            while q and now - q[0] >= self.window:
                q.popleft()

            if len(q) >= self.limit:
                return False

            q.append(now)
            return True

    def reset(self):
        with self._lock:
            self._events.clear()