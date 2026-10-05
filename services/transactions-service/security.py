from typing import Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)

class AuthUser(BaseModel):
    id: int
    role: str
    email: Optional[str] = None
    name: Optional[str] = None

def get_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> AuthUser:
    """
    Extrae y valida la identidad del usuario a partir del token JWT o headers del Gateway.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales de autenticación no válidas o expiradas.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Intentar decodificar token JWT si está presente en Authorization
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            role = payload.get("role")
            email = payload.get("email")
            name = payload.get("name")
            if user_id and role:
                return AuthUser(
                    id=int(user_id),
                    role=str(role),
                    email=email,
                    name=name
                )
        except JWTError:
            pass

    # 2. Alternativa: Headers propagados por el API Gateway (x-user-id, x-user-role)
    gw_user_id = request.headers.get("x-user-id")
    gw_user_role = request.headers.get("x-user-role")
    gw_user_name = request.headers.get("x-user-name")
    gw_user_email = request.headers.get("x-user-email")

    if gw_user_name:
        try:
            import urllib.parse
            gw_user_name = urllib.parse.unquote(gw_user_name)
        except Exception:
            pass

    if gw_user_id and gw_user_role:
        try:
            return AuthUser(
                id=int(gw_user_id),
                role=str(gw_user_role),
                email=gw_user_email,
                name=gw_user_name
            )
        except ValueError:
            pass

    raise credentials_exception

def get_optional_current_user(
    request: Request,
    token: Optional[str] = Depends(oauth2_scheme)
) -> Optional[AuthUser]:
    """Retorna el usuario si está autenticado, o None si es una petición pública anónima"""
    try:
        return get_current_user(request=request, token=token)
    except HTTPException:
        return None

def require_admin(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Valida que el usuario tenga rol de Administrador (Acceso total)"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requieren permisos de Administrador para realizar esta acción."
        )
    return current_user

def require_merchant_or_admin(current_user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Valida que el usuario sea Comercio o Administrador"""
    if current_user.role not in ["merchant", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado: Se requiere perfil de Comercio o Administrador."
        )
    return current_user
