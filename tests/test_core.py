import pytest
import asyncio
from src.core.security.manager import SecretManager, AuthManager
from src.core.services.sdk import with_retry, CircuitBreaker
from pydantic import SecretStr

@pytest.fixture
def secret_manager():
    return SecretManager(master_key="test-key")

def test_secret_encryption_decryption(secret_manager):
    original = "sensitive-data"
    encrypted = secret_manager.encrypt(original)
    assert encrypted != original
    decrypted = secret_manager.decrypt(encrypted)
    assert decrypted == original

def test_secure_credentials(secret_manager):
    creds = {"api_key": SecretStr("raw-key"), "id": "123"}
    secured = secret_manager.secure_credentials(creds)
    assert secret_manager.decrypt(secured["api_key"]) == "raw-key"
    assert secret_manager.decrypt(secured["id"]) == "123"

@pytest.mark.asyncio
async def test_retry_decorator():
    count = 0
    @with_retry(retries=3, backoff=0.01)
    async def failing_func():
        nonlocal count
        count += 1
        if count < 3:
            raise ValueError("Fail")
        return "Success"
    
    result = await failing_func()
    assert result == "Success"
    assert count == 3

@pytest.mark.asyncio
async def test_circuit_breaker():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)
    
    @cb
    async def fail():
        raise ValueError("Error")
    
    # First failure
    with pytest.raises(ValueError):
        await fail()
    assert cb.state == "CLOSED"
    
    # Second failure -> OPEN
    with pytest.raises(ValueError):
        await fail()
    assert cb.state == "OPEN"
    
    # Should block immediately
    with pytest.raises(Exception, match="Circuit breaker is OPEN"):
        await fail()
    
    # Wait for recovery
    await asyncio.sleep(0.15)
    
    # Now in HALF-OPEN, let's make it succeed
    @cb
    async def succeed():
        return "OK"
    
    result = await succeed()
    assert result == "OK"
    assert cb.state == "CLOSED"
