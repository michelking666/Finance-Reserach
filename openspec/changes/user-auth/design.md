# Design: 用户认证

## 数据模型变更

新增 `users` 表：

```sql
CREATE TABLE IF NOT EXISTS users (
    id           SERIAL PRIMARY KEY,
    username     TEXT NOT NULL UNIQUE,
    hashed_password TEXT NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active    BOOLEAN NOT NULL DEFAULT TRUE
);
```

## 认证流程

```
POST /api/auth/login { username, password }
  → db.get_user_by_username(username)
  → auth.verify_password(password, hashed_password)
  → auth.create_access_token({ sub: username })
  → 返回 { access_token, token_type: "bearer" }

所有受保护接口
  → Header: Authorization: Bearer <token>
  → Depends(get_current_user)
  → auth.decode_token(token) → username
  → db.get_user_by_username(username) → User
```

## 新增文件

### `backend/app/services/auth.py`

```python
# JWT 签发/验证（python-jose）
create_access_token(data: dict) -> str
decode_token(token: str) -> str          # 返回 username，失败抛 401

# 密码（passlib bcrypt）
hash_password(plain: str) -> str
verify_password(plain: str, hashed: str) -> bool

# FastAPI Dependency
get_current_user(token: str = Depends(oauth2_scheme)) -> User
```

### `backend/app/routers/auth.py`

```
POST /api/auth/login   → { access_token, token_type }
GET  /api/auth/me      → User（需鉴权）
```

### `backend/scripts/create_user.py`

命令行脚本，用于创建初始用户（无注册接口）：
```bash
python scripts/create_user.py --username admin --password <pwd>
```

## 环境变量

```
JWT_SECRET_KEY=<随机32字节hex>
JWT_EXPIRE_MINUTES=1440   # 默认24小时
```

## 依赖变更

```
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
```

## 前端变更

- 新增 `LoginPage`（用户名/密码表单）
- `localStorage` 存储 token
- `api/client.ts` 所有请求自动附加 `Authorization: Bearer <token>`
- 未登录时重定向到 `/login`
- `NavBar` 显示当前用户名和登出按钮

## CORS 收紧

```python
allow_origins=["http://localhost:5173"]  # 仅本地前端
```

## 集成点

| 文件 | 变更 |
|------|------|
| `db.py` | 追加 users 表 DDL + get_user_by_username + create_user |
| `services/auth.py` | 新增 |
| `routers/auth.py` | 新增 |
| `routers/chat.py` | 添加 Depends(get_current_user) |
| `routers/cards.py` | 添加 Depends(get_current_user) |
| `routers/skills.py` | 添加 Depends(get_current_user) |
| `routers/search.py` | 添加 Depends(get_current_user) |
| `routers/market.py` | 添加 Depends(get_current_user) |
| `main.py` | 注册 auth router，收紧 CORS |
| `requirements.txt` | 新增两个依赖 |
| `.env.example` | 新增 JWT 配置 |
| `scripts/create_user.py` | 新增 |
| `frontend/src/pages/LoginPage.tsx` | 新增 |
| `frontend/src/api/client.ts` | 附加 token |
| `frontend/src/App.tsx` | 路由守卫 |
| `frontend/src/components/NavBar.tsx` | 用户名 + 登出 |
