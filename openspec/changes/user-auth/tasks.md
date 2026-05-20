# Tasks: 用户认证

- [x] 安装依赖：`python-jose[cryptography]`、`passlib[bcrypt]`，更新 requirements.txt
- [x] `db.py`：追加 users 表 DDL + `get_user_by_username`、`create_user` 函数
- [x] 新增 `backend/app/services/auth.py`：JWT 签发/验证、密码哈希/校验、`get_current_user` 依赖
- [x] 新增 `backend/app/routers/auth.py`：POST /api/auth/login、GET /api/auth/me
- [x] 新增 `backend/scripts/create_user.py`：命令行创建用户脚本
- [x] `main.py`：注册 auth router，CORS origins 收紧为 localhost:5173
- [x] 所有业务路由（chat/cards/skills/search/market）添加 `get_current_user` 依赖
- [x] `.env.example`：新增 JWT_SECRET_KEY、JWT_EXPIRE_MINUTES
- [x] 前端：新增 `LoginPage.tsx`，`localStorage` 存 token，`client.ts` 附加 Bearer header
- [x] 前端：`App.tsx` 路由守卫（未登录跳 /login），`NavBar` 显示用户名和登出
- [x] 验证：创建用户，登录获取 token，用 token 访问受保护接口，未登录访问返回 401
