import importlib.util
import inspect
import logging
import os
from typing import Dict, List, Optional, Type
from src.core.domain.base import Connector, ConnectorStatus


logger = logging.getLogger(__name__)


class ConnectorRegistry:
    """Manages dynamic loading and lifecycle of connectors."""

    def __init__(self, connectors_dir: str):
        self.connectors_dir = connectors_dir
        self._connectors: Dict[str, Connector] = {}
        self._connector_classes: Dict[str, Type[Connector]] = {}

    def discover_connectors(self) -> None:
        """Scans the connectors directory for Connector implementations."""
        if not os.path.exists(self.connectors_dir):
            logger.warning(f"Connectors directory {self.connectors_dir} does not exist.")
            return

        for filename in os.listdir(self.connectors_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                file_path = os.path.join(self.connectors_dir, filename)
                self._load_module(module_name, file_path)

    def _load_module(self, module_name: str, file_path: str) -> None:
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj) and
                        hasattr(obj, "metadata") and
                        isinstance(getattr(obj, "metadata"), obj.__annotations__.get("metadata", object)) # Crude check
                        # In real production, we'd use a more robust check or a Base class
                    ):
                        # Add to class registry
                        connector_id = obj.metadata.id
                        self._connector_classes[connector_id] = obj
                        logger.info(f"Discovered connector: {connector_id} ({obj.metadata.name})")
        except Exception as e:
            logger.error(f"Failed to load connector from {file_path}: {e}")

    async def register_instance(self, connector_id: str, instance: Connector) -> None:
        """Manually register an initialized connector instance."""
        await instance.initialize()
        self._connectors[connector_id] = instance

    def get_connector(self, connector_id: str) -> Optional[Connector]:
        return self._connectors.get(connector_id)

    def list_connectors(self) -> List[Connector]:
        return list(self._connectors.values())

    async def shutdown_all(self) -> None:
        for connector in self._connectors.values():
            await connector.shutdown()
        self._connectors.clear()
