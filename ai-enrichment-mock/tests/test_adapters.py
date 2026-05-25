import time
import pytest
import requests_mock
from app.infrastructure.adapters.base_adapter import BaseAdapter, CircuitBreakerOpenException

@pytest.fixture
def adapter():
    return BaseAdapter(
        name="TestAdapter",
        base_url="http://test.api",
        failure_threshold=3,
        cooldown_seconds=2,
        cache_ttl=5,
        timeout=1
    )

def test_cache_hit(adapter, requests_mock):
    requests_mock.get("http://test.api/data", json={"result": "success"})
    
    # First request - cache miss
    result1 = adapter.fetch("/data", cache_kwargs={"q": "test"})
    assert result1["data"]["result"] == "success"
    assert result1["cached"] is False
    assert adapter.cache.get(adapter.normalize_key(q="test")) == {"result": "success"}

    # Second request - cache hit
    result2 = adapter.fetch("/data", cache_kwargs={"q": "test"})
    assert result2["data"]["result"] == "success"
    assert result2["cached"] is True
    
    # Check that only 1 request was made
    assert requests_mock.call_count == 1

def test_404_handling(adapter, requests_mock):
    requests_mock.get("http://test.api/not_found", status_code=404)
    result = adapter.fetch("/not_found", cache_kwargs={"id": "1"})
    assert result["error"] == "not_found"
    assert result["status_code"] == 404
    assert adapter.circuit_breaker.state == "CLOSED"

def test_429_rate_limit_handling(adapter, requests_mock):
    requests_mock.get("http://test.api/rate_limit", status_code=429)
    result = adapter.fetch("/rate_limit", cache_kwargs={"id": "2"})
    assert result["error"] == "rate_limit"
    assert result["status_code"] == 429
    assert adapter.circuit_breaker.failure_count == 1

def test_consecutive_failures_open_circuit(adapter, requests_mock):
    requests_mock.get("http://test.api/error", status_code=500)
    
    # Fail 1
    adapter.fetch("/error", cache_kwargs={"id": "error"})
    assert adapter.circuit_breaker.failure_count == 1
    assert adapter.circuit_breaker.state == "CLOSED"
    
    # Fail 2
    adapter.fetch("/error", cache_kwargs={"id": "error"})
    assert adapter.circuit_breaker.failure_count == 2
    assert adapter.circuit_breaker.state == "CLOSED"
    
    # Fail 3
    adapter.fetch("/error", cache_kwargs={"id": "error"})
    assert adapter.circuit_breaker.failure_count == 3
    assert adapter.circuit_breaker.state == "OPEN"
    
    # Circuit open, next request should raise exception
    with pytest.raises(CircuitBreakerOpenException):
        adapter.fetch("/error", cache_kwargs={"id": "error"})

def test_circuit_recovery_after_cooldown(adapter, requests_mock):
    requests_mock.get("http://test.api/error", status_code=500)
    
    # Open circuit
    for _ in range(3):
        adapter.fetch("/error", cache_kwargs={"id": "error"})
        
    assert adapter.circuit_breaker.state == "OPEN"
    
    # Wait for cooldown
    time.sleep(2.1)
    
    # Check state changes to half open
    state = adapter.circuit_breaker.get_state()
    assert state["state"] == "HALF_OPEN"
    
    # Next successful request closes circuit
    requests_mock.get("http://test.api/error", json={"status": "ok"})
    adapter.fetch("/error", cache_kwargs={"id": "error2"})
    
    assert adapter.circuit_breaker.state == "CLOSED"
    assert adapter.circuit_breaker.failure_count == 0

def test_cache_expiration(adapter, requests_mock):
    requests_mock.get("http://test.api/expire", json={"status": "ok"})
    
    adapter.fetch("/expire", cache_kwargs={"q": "exp"})
    
    # Wait for TTL to expire
    adapter.cache.ttl_seconds = 0
    time.sleep(0.1)
    
    result = adapter.fetch("/expire", cache_kwargs={"q": "exp"})
    assert result["cached"] is False
    assert requests_mock.call_count == 2
