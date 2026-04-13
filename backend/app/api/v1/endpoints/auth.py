from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import httpx
from app.core.config import settings

router = APIRouter()

def get_auth_url(endpoint: str) -> str:
    """Helper to construct the correct Neon Auth URL."""
    base = settings.CLERK_FRONTEND_API.rstrip("/")
    return f"{base}/{endpoint.lstrip('/')}"

@router.post("/login")
async def login_proxy(credentials: Dict[str, Any], request: Request) -> Any:
    """
    Proxies login requests to Neon Auth to avoid CORS issues in Chrome Extension.
    """
    url = get_auth_url("sign-in/email")
    
    # Better Auth requires an Origin header to handle callback URLs correctly
    origin = request.headers.get("origin") or str(request.base_url).rstrip("/")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                json=credentials,
                headers={
                    "Content-Type": "application/json",
                    "Origin": origin
                }
            )
            
            # Forward the response
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Auth Proxy Error: {str(e)}")

@router.post("/signup")
async def signup_proxy(credentials: Dict[str, Any], request: Request) -> Any:
    """
    Proxies signup requests to Neon Auth to avoid CORS issues in Chrome Extension.
    """
    url = get_auth_url("sign-up/email")
    
    origin = request.headers.get("origin") or str(request.base_url).rstrip("/")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                json=credentials,
                headers={
                    "Content-Type": "application/json",
                    "Origin": origin
                }
            )
            
            return JSONResponse(
                status_code=response.status_code,
                content=response.json()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Auth Proxy Error: {str(e)}")

