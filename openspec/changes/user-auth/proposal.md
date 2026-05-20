# Proposal: 用户认证

## 问题

系统当前无任何认证机制，CORS 设置为 `allow_origins=["*"]`，任何人都可以访问所有接口。

## 目标

添加用户名/密码登录，密码 bcrypt 哈希存储，JWT 令牌鉴权，保护所有 `/api/*` 接口。

## 方案

新增 `users` 表和 `auth` 路由。登录成功返回 JWT access token，后续请求通过 `Authorization: Bearer <token>` 鉴权。FastAPI Dependency 注入 `get_current_user`，在需要保护的路由上声明依赖。

密码使用 `bcrypt` 哈希（`passlib[bcrypt]`），禁止明文存储。

## Non-goals

- 不做多因素验证（MFA/TOTP）
- 不做 OAuth / 第三方登录
- 不做 refresh token（access token 有效期内直接用）
- 不做注册接口（用户通过脚本或管理命令创建）
- 不做权限分级（所有登录用户权限相同）

## 影响范围

- `backend/app/services/db.py` — 新增 users 表 DDL 和用户查询函数
- `backend/app/routers/auth.py` — 新增（POST /api/auth/login，POST /api/auth/me）
- `backend/app/services/auth.py` — 新增（JWT 签发/验证，密码哈希/校验，get_current_user 依赖）
- `backend/app/main.py` — 注册 auth router，收紧 CORS origins
- `backend/app/routers/*.py` — 所有路由添加 `get_current_user` 依赖
- `backend/requirements.txt` — 新增 `python-jose[cryptography]`、`passlib[bcrypt]`
- `backend/.env.example` — 新增 `JWT_SECRET_KEY`、`JWT_EXPIRE_MINUTES`
- `frontend/src/api/client.ts` — 请求头附加 Bearer token
- `frontend/src/` — 新增登录页面
