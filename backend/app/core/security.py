import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import httpx
from app.core.config import settings

security = HTTPBearer()

# Cache for JWKS to avoid fetching it on every request
_jwks_cache = None

async def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(settings.NEON_AUTH_JWKS_URL)
                response.raise_for_status()
                _jwks_cache = response.json()
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Could not fetch JWKS: {str(e)}"
                )
    return _jwks_cache

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Verifies the JWT from Neon Auth (Clerk) and returns the user payload.
    """
    token = credentials.credentials
    jwks = await get_jwks()
    
    try:
        # 1. Get the kid from the token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        if not kid:
            raise HTTPException(status_code=401, detail="Missing kid in token header")
        
        # 2. Find the corresponding key in JWKS
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        if not key:
            raise HTTPException(status_code=401, detail="Invalid kid")
            
        # 3. Construct the public key
        # PyJWT can handle the dict format from JWKS directly for certain algorithms
        # or we might need to convert it. Clerk usually uses RS256.
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(key)
        
        # 4. Verify and decode
        # Note: 'azp' (authorized party) is often the frontend client ID
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            # Since Clerk issues tokens, we can verify the issuer if needed
            # options={"verify_aud": False} # Auditor might be different in native apps
        )
        
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
