
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt


SECRET_KEY = "default_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 240


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Crea un token JWT para acceder a los endpoints protegidos."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

print(create_access_token({"user_id": 1}))
