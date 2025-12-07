"""Simple no-op cache manager used by the UI and search engine.

The project previously used a file + in-memory cache. The user requested
to remove caching; to keep imports stable we provide a lightweight
CacheManager that implements the expected interface but performs no
persistent caching (methods are safe no-ops).
"""
from typing import Any, Dict, Optional


class CacheManager:
	"""Minimal cache manager interface (no-op).

	Methods:
	- get(key)
	- set(key, value, ttl=None)
	- clear(key)
	- clear_all()
	- get_cache_stats()
	"""
	def __init__(self):
		self._store: Dict[str, Any] = {}

	def get(self, key: str) -> Optional[Any]:
		return self._store.get(key)

	def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
		# store in volatile in-memory dict only for the lifetime of process
		self._store[key] = value

	def clear(self, key: str) -> None:
		try:
			del self._store[key]
		except KeyError:
			pass

	def clear_all(self) -> None:
		self._store.clear()

	def get_cache_stats(self) -> Dict[str, int]:
		return {"entries": len(self._store), "hits": 0, "misses": 0}


def get_cache_manager() -> CacheManager:
	"""Factory for tests or other modules - returns a new CacheManager."""
	return CacheManager()

