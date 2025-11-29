from fastapi import APIRouter, HTTPException, Header
from typing import Optional

from backend.auth_utils import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
)
from backend.repositories import AuthRepository
from backend.schemas import LoginRequest, UsuarioCreate

router = APIRouter()
auth_repo = AuthRepository()

@router.post("/api/login")
def login(credentials: LoginRequest):
    try:
        user = auth_repo.get_by_username(credentials.username)
        if not user or not verify_password(credentials.password, user["password"]):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        access_token = create_access_token(data={"sub": user["username"], "id": user["id"], "rol": user["rol"]})
        return {"success": True, "token": access_token, "user": {"id": user["id"], "username": user["username"], "rol": user["rol"]}}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/api/register")
def register(user_data: UsuarioCreate):
    try:
        if auth_repo.get_by_username(user_data.username):
            raise HTTPException(status_code=400, detail="El usuario ya existe")
        
        hashed_password = get_password_hash(user_data.password)
        new_id = auth_repo.create_user(user_data, hashed_password)
        return {"message": "Usuario creado exitosamente", "id": new_id}
    except HTTPException: raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

def verify_token(authorization: Optional[str] = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Token no proporcionado")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer': raise HTTPException(status_code=401, detail="Esquema inválido")
        payload = decode_token(token)
        if payload is None: raise HTTPException(status_code=401, detail="Token inválido")
        return payload
    except ValueError: raise HTTPException(status_code=401, detail="Formato inválido")
    except Exception: raise HTTPException(status_code=401, detail="Error verificando token")
