import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("mcp.telemetry")

class TelemetryMiddleware(BaseHTTPMiddleware):
    """Middleware for structured logging and performance tracking."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Extract metadata
        path = request.url.path
        method = request.method
        
        try:
            response = await call_next(request)
            duration = (time.time() - start_time) * 1000
            
            # Structured log
            logger.info(
                f"Request processed | Method: {method} | Path: {path} | "
                f"Status: {response.status_code} | Duration: {duration:.2f}ms"
            )
            
            # In production, we'd emit metrics to Prometheus/Datadog here
            # response.headers["X-Process-Time"] = str(duration)
            
            return response
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            logger.error(
                f"Request failed | Method: {method} | Path: {path} | "
                f"Error: {str(e)} | Duration: {duration:.2f}ms"
            )
            raise e

def setup_logging():
    """Configures structured logging for the entire framework."""
    logging.basicConfig(
        level=logging.INFO,
        format='{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}',
        datefmt='%Y-%m-%dT%H:%M:%S'
    )
