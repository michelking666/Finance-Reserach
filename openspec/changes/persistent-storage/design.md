# Design: 持久化存储

## 数据模型变更

新增 `cards` 表，存储 TopicCard 的全部字段，JSON 列存储嵌套结构。

```sql
CREATE TABLE IF NOT EXISTS cards (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    subtitle    TEXT,
    summary     TEXT NOT NULL,
    tags        JSONB NOT NULL DEFAULT '[]',
    metrics     JSONB NOT NULL DEFAULT '[]',
    bullets     JSONB NOT NULL DEFAULT '[]',
    scenario    TEXT,
    sources     JSONB NOT NULL DEFAULT '[]',
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    saved       BOOLEAN NOT NULL DEFAULT FALSE
);
```

TopicCard 的嵌套字段（tags、metrics、bullets、sources）用 JSONB 存储，读取时通过 Pydantic 反序列化还原。

## db.py 变更

在现有 `_DDL` 中追加 cards 表定义。新增以下函数：

```python
def upsert_card(card: dict) -> None
def get_card(card_id: str) -> dict | None
def list_cards(only_saved: bool = False) -> list[dict]
def delete_card(card_id: str) -> bool
def toggle_save(card_id: str, saved: bool) -> dict | None
```

所有函数在 `_pool is None`（数据库未初始化）时静默降级，返回空值，保持与内存模式的兼容性。

## store.py 变更

`_Store` 的卡片方法改为调用 `db.*` 函数，技能方法不变。

数据库可用时走 PostgreSQL，不可用时（`_pool is None`）降级到内存 dict，保证开发环境无 DB 也能运行。

```
store.list_cards()    → db.list_cards()    (降级: 内存 dict)
store.get_card()      → db.get_card()      (降级: 内存 dict)
store.upsert_card()   → db.upsert_card()   (降级: 内存 dict)
store.delete_card()   → db.delete_card()   (降级: 内存 dict)
store.toggle_save()   → db.toggle_save()   (降级: 内存 dict)
```

## 序列化策略

TopicCard → dict（存入 DB）：`card.model_dump(mode="json")`

dict → TopicCard（从 DB 读出）：`TopicCard.model_validate(row)`

sources 字段中的 Source 对象通过 Pydantic 自动处理嵌套序列化。

## 集成点

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `backend/app/services/db.py` | 修改 | 追加 cards DDL + 5 个 CRUD 函数 |
| `backend/app/services/store.py` | 修改 | 卡片方法委托给 db，保留内存降级 |

无其他文件需要改动。
