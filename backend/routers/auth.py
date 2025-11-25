from fastapi import APIRouter, HTTPException, Depends, Header
from database import get_db_connection
from schemas import LoginRequest, UsuarioCreate
from auth_utils import verify_password, get_password_hash, create_access_token, decode_token
from typing import Optional

router = APIRouter()

@router.post("/api/login")
def login(credentials: LoginRequest):
    """Autenticación de usuario con JWT"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Buscar usuario por username
        query = "SELECT * FROM usuarios WHERE username = %s"
        cursor.execute(query, (credentials.username,))
        user = cursor.fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        # Verificar contraseña hasheada
        if not verify_password(credentials.password, user["password"]):
            raise HTTPException(status_code=401, detail="Credenciales incorrectas")

        # Crear token JWT
        access_token = create_access_token(
            data={
                "sub": user["username"],
                "id": user["id"],
                "rol": user["rol"]
            }
        )

        return {
            "success": True,
            "token": access_token,
            "user": {
                "id": user["id"],
                "username": user["username"],
                "rol": user["rol"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@router.post("/api/register")
def register(user_data: UsuarioCreate):
    """Registro de nuevo usuario"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verificar si el usuario ya existe
        cursor.execute("SELECT id FROM usuarios WHERE username = %s", (user_data.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="El usuario ya existe")

        # Hashear la contraseña
        hashed_password = get_password_hash(user_data.password)

        # Insertar nuevo usuario
        query = """
            INSERT INTO usuarios (username, password, rol)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (user_data.username, hashed_password, user_data.rol or 'usuario'))
        conn.commit()

        return {"message": "Usuario creado exitosamente", "id": cursor.lastrowid}

    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear usuario: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def verify_token(authorization: Optional[str] = Header(None)):
    """Middleware para verificar el token JWT"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token no proporcionado")

    try:
        # Extraer el token del header "Bearer <token>"
        scheme, token = authorization.split()
        if scheme.lower() != 'bearer':
            raise HTTPException(status_code=401, detail="Esquema de autenticación inválido")

        payload = decode_token(token)
        if payload is None:
            raise HTTPException(status_code=401, detail="Token inválido o expirado")

        return payload
    except ValueError:
        raise HTTPException(status_code=401, detail="Formato de token inválido")
    except Exception:
        raise HTTPException(status_code=401, detail="Error al verificar token")