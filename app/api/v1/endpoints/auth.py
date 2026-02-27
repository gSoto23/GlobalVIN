from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

router = APIRouter()
security = HTTPBearer(auto_error=False)

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Mock JWT verifier for local testing.
    In Phase 4 this will properly validate RSA signatures/secrets.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere token Bearer para accesar esta ruta comercial",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"sub": "test_user_from_dashboard"}

@router.get("/me")
async def get_current_user_debug(token_data: dict = Depends(verify_token)):
    """
    Endpoint de depuración para probar JWT.
    """
    return {"user": token_data}
