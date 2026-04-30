from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.auth.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(
            token, settings.auth.secret_key, algorithms=[settings.auth.algorithm]
        )
        return decoded_token
    except jwt.PyJWTError:
        return None
