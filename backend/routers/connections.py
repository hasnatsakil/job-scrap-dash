from fastapi import APIRouter, HTTPException
from backend.services.connection_manager import connection_manager

router = APIRouter(prefix="/connections", tags=["connections"])

@router.get("")
async def get_connections():
    """Get the status of all registered connections."""
    statuses = await connection_manager.get_all_statuses()
    return {"connections": statuses}

@router.post("/{provider_id}/connect")
async def connect_provider(provider_id: str):
    """Initiate a connection flow for a specific provider."""
    connector = connection_manager.get_connector(provider_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Provider not found")

    result = await connector.connect()
    if result.get("status") == "Error":
        raise HTTPException(status_code=400, detail=result.get("message"))

    return {"status": "success", "message": "Successfully connected"}

@router.post("/{provider_id}/disconnect")
async def disconnect_provider(provider_id: str):
    connector = connection_manager.get_connector(provider_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Provider not found")

    await connector.disconnect()
    return {"status": "success"}

@router.post("/{provider_id}/validate")
async def validate_provider(provider_id: str):
    connector = connection_manager.get_connector(provider_id)
    if not connector:
        raise HTTPException(status_code=404, detail="Provider not found")

    is_valid = await connector.validate()
    return {"status": "success", "valid": is_valid}
