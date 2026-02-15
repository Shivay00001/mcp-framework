import abc
import httpx
import logging
import time
from typing import Any, Dict, Optional
from src.core.domain.base import Connector, ConnectorMetadata, UnifiedRequest, UnifiedResponse, ConnectorStatus
from src.core.services.sdk import with_retry, CircuitBreaker


logger = logging.getLogger(__name__)


class BaseConnector(Connector, abc.ABC):
    """Abstract base class for all connectors, providing common utilities."""

    def __init__(self, metadata: ConnectorMetadata):
        self.metadata = metadata
        self.client: Optional[httpx.AsyncClient] = None
        self._circuit_breaker = CircuitBreaker()

    async def initialize(self) -> None:
        """Default initialization: creates an async HTTP client."""
        self.client = httpx.AsyncClient(timeout=30.0)
        self.metadata.status = ConnectorStatus.RUNNING
        logger.info(f"Connector {self.metadata.id} initialized.")

    async def shutdown(self) -> None:
        """Default shutdown: closes the async HTTP client."""
        if self.client:
            await self.client.aclose()
        self.metadata.status = ConnectorStatus.IDLE
        logger.info(f"Connector {self.metadata.id} shut down.")

    async def health_check(self) -> bool:
        """Override this for specific health check logic."""
        return self.metadata.status == ConnectorStatus.RUNNING

    async def handle_webhook(self, data: Any, headers: Dict[str, str]) -> Dict[str, Any]:
        """Default webhook handler (to be overridden)."""
        logger.info(f"Received webhook for {self.metadata.id}")
        return {"status": "received"}

    @abc.abstractmethod
    async def _handle_request(self, request: UnifiedRequest) -> UnifiedResponse:
        """Actual request handling logic to be implemented by subclasses."""
        ...

    async def execute(self, request: UnifiedRequest) -> UnifiedResponse:
        """Unified execution entry point with telemetry and circuit breaking."""
        start_time = time.time()
        try:
            # Wrap handle_request with circuit breaker
            response = await self._circuit_breaker(self._handle_request)(request)
            response.latency_ms = (time.time() - start_time) * 1000
            return response
        except Exception as e:
            logger.error(f"Execution error in {self.metadata.id}: {e}")
            return UnifiedResponse(
                success=False,
                error=str(e),
                latency_ms=(time.time() - start_time) * 1000
            )
