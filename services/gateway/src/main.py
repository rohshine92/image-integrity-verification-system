from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import httpx
import time
from typing import Dict, Optional, Any

app = FastAPI(title="Gateway Service")

class HealthResponse(BaseModel):
    service: str
    status: str
    dependencies: Optional[Dict[str, Dict[str, Any]]] = None

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Gateway service health check that monitors all dependent services"""
    dependencies = {}
    overall_status = "healthy"
    
    # Check API service health
    api_health = await check_service_health("api", 8000, "api-service")
    dependencies["api-service"] = api_health
    
    # Check verification service health
    verification_health = await check_service_health("verification", 8001, "verification-service")
    dependencies["verification-service"] = verification_health
    
    # Determine overall status
    if any(dep["status"] != "healthy" for dep in dependencies.values()):
        overall_status = "unhealthy"
    
    response = HealthResponse(
        service="gateway-service",
        status=overall_status,
        dependencies=dependencies
    )
    
    if overall_status == "unhealthy":
        raise HTTPException(status_code=503, detail=response.dict())
    
    return response

async def check_service_health(service_name: str, port: int, display_name: str) -> Dict[str, Any]:
    """Helper function to check health of a dependent service"""
    start_time = time.time()
    url = f"http://{service_name}:{port}/health"
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response_time = int((time.time() - start_time) * 1000)
            
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "response_time_ms": response_time
                }
            else:
                return {
                    "status": "unhealthy",
                    "response_time_ms": response_time,
                    "error": f"HTTP {response.status_code}"
                }
    except Exception as e:
        response_time = int((time.time() - start_time) * 1000)
        return {
            "status": "unhealthy",
            "response_time_ms": response_time,
            "error": str(e)
        }

@app.post("/verify")
async def verify_image(image_url: str):
    """Coordinate image verification across services"""
    return {"message": "Image verification process initiated", "image_url": image_url}