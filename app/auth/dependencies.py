"""Dependencia de autenticación para los router."""
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.auth.jwt import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """Obtiene los datos del usuario a partir de un token JWT."""
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload
