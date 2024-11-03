import jwt

from fastapi import HTTPException
from datetime import datetime, timedelta

from apps.libs.config.core_config import core_config


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=core_config.jwt_expiration_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, core_config.jwt_secret, algorithm=core_config.jwt_algorithm)
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, core_config.jwt_secret, algorithms=[core_config.jwt_algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Токен истек.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Недействительный токен.")
