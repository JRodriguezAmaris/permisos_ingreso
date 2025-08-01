"""Modulo de autenticación."""
from datetime import datetime, timezone
from jose import JWTError, jwt
from app.config.settings import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"


def decode_access_token(token: str) -> dict | None:
    """Decodifica un token JWT."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if datetime.fromtimestamp(payload["exp"], tz=timezone.utc) < datetime.now(timezone.utc):
            return None
        return payload
    except JWTError:
        return None
