"""JWT 签发/验证、密码哈希、FastAPI 鉴权依赖。"""
from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from app.services import db

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-production")
_ALGORITHM = "HS256"
_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(username: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=_EXPIRE_MINUTES)
    return jwt.encode({"sub": username, "exp": expire}, _SECRET_KEY, algorithm=_ALGORITHM)


def _decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
        username: str | None = payload.get("sub")
        if not username:
            raise ValueError
        return username
    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效或已过期的令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(token: str = Depends(_oauth2_scheme)) -> dict:
    username = _decode_token(token)
    user = db.get_user_by_username(username)
    if not user or not user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已禁用")
    return user
