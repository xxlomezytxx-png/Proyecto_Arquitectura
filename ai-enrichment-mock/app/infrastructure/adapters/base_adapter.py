import time
import requests
from typing import Dict, Any, Optional

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, failure_threshold: int = 3, cooldown_seconds: int = 60):
        self.failure_threshold = failure_threshold
        self.cooldown_seconds = cooldown_seconds
        self.failure_count = 0
        self.state = "CLOSED"
        self.last_failure_time: float = 0.0

    def record_failure(self):
        self.failure_count += 1
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            self.last_failure_time = time.time()

    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"

    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.cooldown_seconds:
                self.state = "HALF_OPEN"
                return True
            return False
        if self.state == "HALF_OPEN":
            return True
        return False

    def get_state(self) -> Dict[str, Any]:
        if self.state == "OPEN" and (time.time() - self.last_failure_time) >= self.cooldown_seconds:
            self.state = "HALF_OPEN"
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "cooldown_seconds": self.cooldown_seconds
        }

class SimpleCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry["timestamp"] <= self.ttl_seconds:
                return entry["data"]
            else:
                del self.cache[key]
        return None

    def set(self, key: str, value: Any):
        self.cache[key] = {
            "timestamp": time.time(),
            "data": value
        }

    def clear(self):
        self.cache.clear()

class BaseAdapter:
    def __init__(self, name: str, base_url: str, failure_threshold: int = 3, cooldown_seconds: int = 60, cache_ttl: int = 300, timeout: int = 5):
        self.name = name
        self.base_url = base_url
        self.circuit_breaker = CircuitBreaker(failure_threshold, cooldown_seconds)
        self.cache = SimpleCache(cache_ttl)
        self.timeout = timeout

    def normalize_key(self, **kwargs) -> str:
        key_parts = []
        for k, v in sorted(kwargs.items()):
            if v:
                key_parts.append(f"{k}:{str(v).strip().lower()}")
        return f"{self.name}_" + "_".join(key_parts)

    def _execute_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        if not self.circuit_breaker.can_execute():
            raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {self.name}")

        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(method, url, timeout=self.timeout, **kwargs)
            if response.status_code == 429:
                self.circuit_breaker.record_failure()
                return {"error": "rate_limit", "status_code": 429}
            if response.status_code == 404:
                self.circuit_breaker.record_success()
                return {"error": "not_found", "status_code": 404}
            
            response.raise_for_status()
            
            if self.circuit_breaker.state == "HALF_OPEN":
                self.circuit_breaker.record_success()
            
            try:
                return {"data": response.json(), "status_code": response.status_code}
            except ValueError:
                return {"data": response.text, "status_code": response.status_code}
                
        except requests.exceptions.RequestException as e:
            self.circuit_breaker.record_failure()
            return {"error": "request_failed", "detail": str(e)}

    def fetch(self, endpoint: str, cache_kwargs: Dict[str, Any], **request_kwargs) -> Dict[str, Any]:
        cache_key = self.normalize_key(**cache_kwargs)
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return {"data": cached_result, "cached": True}

        result = self._execute_request("GET", endpoint, **request_kwargs)
        if "error" not in result:
            self.cache.set(cache_key, result.get("data"))
            result["cached"] = False
        return result

    def get_status(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "base_url": self.base_url,
            "circuit_breaker": self.circuit_breaker.get_state(),
            "cache_items": len(self.cache.cache)
        }
