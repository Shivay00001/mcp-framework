from enum import Enum
from typing import Any, Dict, List, Optional, Protocol, Union
from pydantic import BaseModel, Field, SecretStr


class AuthType(str, Enum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BEARER = "bearer"
    BASIC = "basic"
    NONE = "none"


class ConnectorStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    ERROR = "error"
    DISABLED = "disabled"


class HttpMethod(str, Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


class UnifiedRequest(BaseModel):
    """Normalized request format for all connectors."""
    action: str
    params: Dict[str, Any] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UnifiedResponse(BaseModel):
    """Normalized response format for all connectors."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    raw_response: Optional[Dict[str, Any]] = None
    latency_ms: float = 0.0


class AuthConfig(BaseModel):
    auth_type: AuthType
    credentials: Dict[str, Union[str, SecretStr]] = Field(default_factory=dict)
    refresh_token_url: Optional[str] = None


class ConnectorMetadata(BaseModel):
    id: str
    name: str
    version: str
    description: str
    supported_actions: List[str]
    auth_config: AuthConfig
    status: ConnectorStatus = ConnectorStatus.IDLE
    health_score: float = 100.0


class Connector(Protocol):
    """Base interface for all connectors."""
    metadata: ConnectorMetadata

    async def initialize(self) -> None:
        """Connect to the platform, verify auth, etc."""
        ...

    async def execute(self, request: UnifiedRequest) -> UnifiedResponse:
        """Execute a specific action on the platform."""
        ...

    async def shutdown(self) -> None:
        """Closes any sessions/connections."""
        ...

    async def health_check(self) -> bool:
        """Verify the health of the connection."""
        ...

    async def handle_webhook(self, data: Any, headers: Dict[str, str]) -> Dict[str, Any]:
        """Handle incoming webhooks from external platforms."""
        ...
