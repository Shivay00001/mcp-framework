import asyncio
import logging
from fastapi import FastAPI
from src.api.routes import router as api_router
import src.api.routes as routes
from src.core.config import settings
from src.infrastructure.registry.manager import ConnectorRegistry
from src.core.security.manager import SecretManager
from src.infrastructure.messaging.bus import EventBus
from src.infrastructure.connectors.openai import OpenAIConnector
from src.infrastructure.connectors.stripe import StripeConnector
from src.infrastructure.monitoring.telemetry import TelemetryMiddleware, setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.app_name, version=settings.version)
app.add_middleware(TelemetryMiddleware)

@app.on_event("startup")
async def startup_event():
    # Initialize services
    secret_manager = SecretManager(master_key=settings.master_key)
    registry = ConnectorRegistry(connectors_dir=settings.connectors_dir)
    bus = EventBus()

    # In a real scenario, we'd load these from a DB or config
    # For demonstration, we manually register the example connectors
    # with dummy keys (secured via secret_manager)
    openai = OpenAIConnector(api_key="sk-dummy-openai-key")
    stripe = StripeConnector(api_key="sk_test_dummy_stripe_key")

    await registry.register_instance("openai", openai)
    await registry.register_instance("stripe", stripe)

    # Wire up to routes
    routes.registry = registry
    routes.bus = bus

    # Start event bus in background
    asyncio.create_task(bus.start())
    
    logger.info("MCP Framework started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    if routes.registry:
        await routes.registry.shutdown_all()
    logger.info("MCP Framework shut down")

app.include_router(api_router, prefix="/api/v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
