from datetime import datetime
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.params import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from typing_extensions import Annotated

from app.api.v1.auth.jwt import decode_token
from app.api.v1.users.schemas import RefreshToken

http_bearer = HTTPBearer()


def get_payload_from_refresh_token_from_json(token: RefreshToken) -> dict[str, datetime | str]:
    """Получает payload из refresh токена содержащегося в json."""
    return decode_token(token.refresh_token)


def user_id_from_refresh_token(payload: Annotated[dict, Depends(get_payload_from_refresh_token_from_json)]) -> UUID:
    """Получает user_id из refresh токена."""
    if payload.get("token_type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Тип токена должен быть 'refresh'")
    return UUID(payload["sub"])


async def get_current_user_id(credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)]) -> UUID:
    """Получает User_id из токена."""
    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Некорректный токен")
    if payload["token_type"] != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Тип токена должен быть 'access'")
    return UUID(payload["sub"])
