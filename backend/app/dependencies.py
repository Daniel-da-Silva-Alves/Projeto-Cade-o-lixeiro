"""
Cadê o Lixeiro? v2.0 — FastAPI Dependencies

Funções de dependência reutilizáveis para injeção em routers.
Suporte a JWT ES256 do Supabase via JWKS (chave pública).
"""

import httpx
import jwt as pyjwt
from functools import lru_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db  # noqa: F401 — re-export

settings = get_settings()
security = HTTPBearer()

# Cache da chave pública JWKS do Supabase
_jwks_client = None


def _get_jwks_client():
    """Retorna um PyJWKClient cacheado para o JWKS do Supabase."""
    global _jwks_client
    if _jwks_client is None:
        jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        _jwks_client = pyjwt.PyJWKClient(jwks_url)
    return _jwks_client


class CurrentUser:
    """Dados do usuário extraídos do JWT."""

    def __init__(self, id: str, email: str, role: str = "authenticated"):
        self.id = id
        self.email = email
        self.role = role


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> CurrentUser:
    """
    Decodifica o JWT do Supabase e retorna o usuário autenticado.
    Compatível com ES256 (JWKS) e HS256 (JWT_SECRET legado).
    """
    token = credentials.credentials
    try:
        # Tenta primeiro via JWKS (ES256 — Supabase v2+)
        jwks_client = _get_jwks_client()
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = pyjwt.decode(
            token,
            signing_key.key,
            algorithms=["ES256"],
            audience="authenticated",
            leeway=60,  # Tolera 60s de clock skew
        )
    except Exception:
        try:
            # Fallback para HS256 (JWT_SECRET — Supabase v1 / local)
            payload = pyjwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=["HS256"],
                audience="authenticated",
                leeway=60,
            )
        except pyjwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token inválido: {str(e)}",
                headers={"WWW-Authenticate": "Bearer"},
            )

    user_id: str = payload.get("sub")
    email: str = payload.get("email", "")
    role: str = payload.get("role", "authenticated")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido: 'sub' ausente",
        )

    return CurrentUser(id=user_id, email=email, role=role)


async def require_admin(
    user: CurrentUser = Depends(get_current_user),
) -> CurrentUser:
    """Garante que o usuário tem role 'admin' ou 'service_role'."""
    if user.role not in ("admin", "service_role"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    return user
