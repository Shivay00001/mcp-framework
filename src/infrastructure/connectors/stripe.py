from typing import Any, Dict
from src.core.domain.base import UnifiedRequest, UnifiedResponse, ConnectorMetadata, AuthConfig, AuthType
from src.infrastructure.connectors.base import BaseConnector


class StripeConnector(BaseConnector):
    """Connector for Stripe API."""

    def __init__(self, api_key: str):
        metadata = ConnectorMetadata(
            id="stripe",
            name="Stripe",
            version="1.0.0",
            description="Payment processing via Stripe",
            supported_actions=["create_charge", "list_customers"],
            auth_config=AuthConfig(
                auth_type=AuthType.API_KEY,
                credentials={"api_key": api_key}
            )
        )
        super().__init__(metadata)

    async def _handle_request(self, request: UnifiedRequest) -> UnifiedResponse:
        if request.action == "create_charge":
            return await self._create_charge(request.params)
        elif request.action == "list_customers":
            return await self._list_customers(request.params)
        else:
            raise ValueError(f"Action {request.action} not supported by Stripe connector")

    async def _create_charge(self, params: Dict[str, Any]) -> UnifiedResponse:
        # In a real implementation, we would use stripe-python or direct REST
        response = await self.client.post(
            "https://api.stripe.com/v1/charges",
            data=params,  # Stripe uses form-encoded
            auth=(self.metadata.auth_config.credentials['api_key'], "")
        )
        # Handle error responses, etc.
        return UnifiedResponse(
            success=response.status_code < 400,
            data=response.json() if response.status_code < 400 else None,
            error=response.text if response.status_code >= 400 else None,
            raw_response=response.json()
        )

    async def _list_customers(self, params: Dict[str, Any]) -> UnifiedResponse:
        response = await self.client.get(
            "https://api.stripe.com/v1/customers",
            params=params,
            auth=(self.metadata.auth_config.credentials['api_key'], "")
        )
        return UnifiedResponse(
            success=response.status_code < 400,
            data=response.json() if response.status_code < 400 else None,
            error=response.text if response.status_code >= 400 else None,
            raw_response=response.json()
        )
