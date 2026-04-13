from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Request
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
            
            data = response.json()
            
            # If successful, try to find a session token in cookies if not in body
            if response.status_code == 200:
                # Look for Clerk session cookie
                session_cookie = response.cookies.get("__session") or response.cookies.get("__clerk_db_jwt")
                if session_cookie and "token" not in data:
                    data["token"] = session_cookie
                    
            return JSONResponse(
                status_code=response.status_code,
                content=data
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
            
            data = response.json()
            
            # If successful, try to find a session token in cookies if not in body
            if response.status_code == 200:
                # Look for Clerk session cookie
                session_cookie = response.cookies.get("__session") or response.cookies.get("__clerk_db_jwt")
                if session_cookie and "token" not in data:
                    data["token"] = session_cookie
                    
            return JSONResponse(
                status_code=response.status_code,
                content=data
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Auth Proxy Error: {str(e)}")

