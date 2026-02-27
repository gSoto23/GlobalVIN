from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

router = APIRouter()
security = HTTPBearer(auto_error=False)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Validates the Bearer token signature and expiration according to RACSA standards.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"codigo": "AUTH_001", "mensaje": "Token no provisto o esquema invalido", "detalle": "Se requiere token Bearer", "correlationId": "TBD"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"codigo": "AUTH_002", "mensaje": "Token invalido", "detalle": "No se encontro el sujeto (sub)", "correlationId": "TBD"},
            )
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"codigo": "AUTH_003", "mensaje": "Token invalido o expirado", "detalle": str(e), "correlationId": "TBD"},
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/token")
async def login_for_access_token():
    """
    Endpoint para generar un token de prueba en desarrollo. 
    En producción, RACSA tendrá su propio Servidor de Identidad (IdP).
    """
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": "racsa_validator", "scopes": ["read:vehiculos"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
async def get_current_user_debug(token_data: dict = Depends(verify_token)):
    """
    Endpoint de depuración para probar el Payload extraido del JWT validado.
    """
    return {"valido": True, "token_payload": token_data}
