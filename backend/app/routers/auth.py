"""认证接口：登录、当前用户信息。"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.services import auth as auth_svc
from app.services import db

router = APIRouter(prefix="/api/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool


@router.post("/login", response_model=TokenResponse)
def login(form: OAuth2PasswordRequestForm = Depends()) -> TokenResponse:
    user = db.get_user_by_username(form.username)
    if not user or not auth_svc.verify_password(form.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.get("is_active"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已禁用")
    token = auth_svc.create_access_token(user["username"])
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(auth_svc.get_current_user)) -> UserResponse:
    return UserResponse(**current_user)
