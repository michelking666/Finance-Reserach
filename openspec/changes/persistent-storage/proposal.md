# Proposal: 持久化存储

## 问题

`services/store.py` 使用内存存储，进程重启后所有话题卡片丢失。用户收藏的卡片无法跨会话保留。

## 目标

将话题卡片（TopicCard）持久化到 PostgreSQL，保持 `store` 的接口契约不变，上层代码零感知。

## 方案

在 `db.py` 中新增 `cards` 表，将 `_Store` 的卡片方法改为读写 PostgreSQL。技能保持内存加载，不变。

## Non-goals

- 不迁移技能到数据库（技能是静态配置）
- 不引入 ORM（继续用 psycopg2 裸 SQL）
- 不做数据库迁移工具（直接 CREATE TABLE IF NOT EXISTS）
- 不做卡片分页（当前数量级不需要）

## 影响范围

- `backend/app/services/store.py` — 卡片方法改为 PostgreSQL 读写
- `backend/app/services/db.py` — 新增 cards 表 DDL 和 CRUD 函数
- `backend/app/models.py` — TopicCard 无需改动（Pydantic 序列化/反序列化）
- `backend/requirements.txt` — 无新依赖（psycopg2-binary 已有）
