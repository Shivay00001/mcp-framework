# MCP Framework

A production-grade Multi-Platform Connector Platform (MCP) built with Python and FastAPI.

## Features

- **Clean Architecture**: Decoupled core domain from infrastructure.
- **Plugin System**: Dynamic connector loading from directories.
- **Security**: AES-256 credential encryption and OAuth2/API-Key management.
- **Resilience**: Integrated retry strategies (exponential backoff) and circuit breakers.
- **Observability**: Structured logging and request telemetry.
- **CLI**: Management tool for listing and testing connectors.

## Installation

```bash
pip install mcp-framework-sdk  # Note: Package name on PyPI
```

## Quick Start

1. **Initialize the Server**:

   ```bash
   uvicorn src.api.main:app --host 0.0.0.0 --port 8000
   ```

2. **Use the CLI**:

   ```bash
   python src/cli/main.py list
   ```

## Development

To add a new connector, subclass `BaseConnector` in `src/infrastructure/connectors/`:

```python
from src.infrastructure.connectors.base import BaseConnector

class MyConnector(BaseConnector):
    # Implement actions...
    pass
```

## License

MIT
