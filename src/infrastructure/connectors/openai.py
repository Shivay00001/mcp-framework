from typing import Any, Dict
from src.core.domain.base import UnifiedRequest, UnifiedResponse, ConnectorMetadata, AuthConfig, AuthType
from src.infrastructure.connectors.base import BaseConnector
from src.core.services.sdk import with_retry


class OpenAIConnector(BaseConnector):
    """Connector for OpenAI API."""

    def __init__(self, api_key: str):
        metadata = ConnectorMetadata(
            id="openai",
            name="OpenAI",
            version="1.0.0",
            description="Access OpenAI GPT models",
            supported_actions=["chat_completion", "embeddings"],
            auth_config=AuthConfig(
                auth_type=AuthType.API_KEY,
                credentials={"api_key": api_key}
            )
        )
        super().__init__(metadata)

    @with_retry(retries=3)
    async def _handle_request(self, request: UnifiedRequest) -> UnifiedResponse:
        if request.action == "chat_completion":
            return await self._chat_completion(request.params)
        elif request.action == "embeddings":
            return await self._embeddings(request.params)
        else:
            raise ValueError(f"Action {request.action} not supported by OpenAI connector")

    async def _chat_completion(self, params: Dict[str, Any]) -> UnifiedResponse:
        response = await self.client.post(
            "https://api.openai.com/v1/chat/completions",
            json=params,
            headers={"Authorization": f"Bearer {self.metadata.auth_config.credentials['api_key']}"}
        )
        response.raise_for_status()
        return UnifiedResponse(
            success=True,
            data=response.json(),
            raw_response=response.json()
        )

    async def _embeddings(self, params: Dict[str, Any]) -> UnifiedResponse:
        response = await self.client.post(
            "https://api.openai.com/v1/embeddings",
            json=params,
            headers={"Authorization": f"Bearer {self.metadata.auth_config.credentials['api_key']}"}
        )
        response.raise_for_status()
        return UnifiedResponse(
            success=True,
            data=response.json(),
            raw_response=response.json()
        )
