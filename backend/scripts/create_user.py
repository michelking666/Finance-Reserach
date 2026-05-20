"""命令行工具：创建初始用户。

用法：
    cd backend
    /usr/local/bin/python3.11 scripts/create_user.py --username admin --password <密码>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 把 backend/ 加入 path，使 app.* 可导入
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from app.services import db
from app.services.auth import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(description="创建用户")
    parser.add_argument("--username", required=True)
    parser.add_argument("--password", required=True)
    args = parser.parse_args()

    db.init()

    existing = db.get_user_by_username(args.username)
    if existing:
        print(f"用户 '{args.username}' 已存在")
        sys.exit(1)

    hashed = hash_password(args.password)
    user = db.create_user(args.username, hashed)
    print(f"用户创建成功：id={user['id']} username={user['username']}")


if __name__ == "__main__":
    main()
