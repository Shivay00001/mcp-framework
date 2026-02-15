from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from src.core.domain.base import UnifiedRequest, UnifiedResponse, ConnectorMetadata
from src.infrastructure.registry.manager import ConnectorRegistry
from src.core.config import settings
from src.infrastructure.messaging.bus import EventBus

router = APIRouter()

# Global instances (to be initialized in main.py)
registry: ConnectorRegistry = None
bus: EventBus = None

def get_registry() -> ConnectorRegistry:
    return registry

def get_bus() -> EventBus:
    return bus

@router.get("/connectors", response_model=List[ConnectorMetadata])
async def list_connectors(reg: ConnectorRegistry = Depends(get_registry)):
    return [c.metadata for c in reg.list_connectors()]

@router.post("/execute/{connector_id}", response_model=UnifiedResponse)
async def execute_action(
    connector_id: str,
    request: UnifiedRequest,
    background_tasks: BackgroundTasks,
    reg: ConnectorRegistry = Depends(get_registry),
    event_bus: EventBus = Depends(get_bus)
):
    connector = reg.get_connector(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    # Execute action
    response = await connector.execute(request)
    
    # Log event asynchronously
    background_tasks.add_task(
        event_bus.publish, 
        "action_executed", 
        {"connector_id": connector_id, "action": request.action, "success": response.success}
    )
    
    return response

@router.post("/webhooks/{connector_id}")
async def handle_webhook(
    connector_id: str,
    request: dict,
    headers: dict = {},
    reg: ConnectorRegistry = Depends(get_registry)
):
    connector = reg.get_connector(connector_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    return await connector.handle_webhook(request, headers)

@router.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.version}
