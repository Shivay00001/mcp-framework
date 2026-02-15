import pytest
import os
from src.infrastructure.registry.manager import ConnectorRegistry
from src.core.domain.base import ConnectorMetadata, AuthConfig, AuthType, UnifiedRequest, UnifiedResponse
from src.infrastructure.connectors.base import BaseConnector

class MockConnector(BaseConnector):
    def __init__(self):
        metadata = ConnectorMetadata(
            id="mock",
            name="Mock",
            version="1.0.0",
            description="Mock",
            supported_actions=["test"],
            auth_config=AuthConfig(auth_type=AuthType.NONE)
        )
        super().__init__(metadata)
    
    async def _handle_request(self, request: UnifiedRequest) -> UnifiedResponse:
        return UnifiedResponse(success=True, data={"echo": request.params})

@pytest.mark.asyncio
async def test_registry_registration():
    registry = ConnectorRegistry(connectors_dir="./connectors")
    mock = MockConnector()
    await registry.register_instance("mock", mock)
    
    retrieved = registry.get_connector("mock")
    assert retrieved is not None
    assert retrieved.metadata.id == "mock"
    
    response = await retrieved.execute(UnifiedRequest(action="test", params={"foo": "bar"}))
    assert response.success is True
    assert response.data["echo"]["foo"] == "bar"

@pytest.mark.asyncio
async def test_registry_discovery(tmp_path):
    # Create a dummy connector file
    conn_dir = tmp_path / "connectors"
    conn_dir.mkdir()
    conn_file = conn_dir / "test_conn.py"
    conn_file.write_text("""
from src.core.domain.base import ConnectorMetadata, AuthConfig, AuthType
from src.infrastructure.connectors.base import BaseConnector

class TestConnector(BaseConnector):
    metadata = ConnectorMetadata(
        id="test_disc",
        name="Test Discovery",
        version="1.0.0",
        description="Test",
        supported_actions=[],
        auth_config=AuthConfig(auth_type=AuthType.NONE)
    )
    def __init__(self):
        super().__init__(self.metadata)
    async def _handle_request(self, req):
        pass
""")
    
    registry = ConnectorRegistry(connectors_dir=str(conn_dir))
    registry.discover_connectors()
    
    # Check if discovered class is in the class registry
    assert "test_disc" in registry._connector_classes
