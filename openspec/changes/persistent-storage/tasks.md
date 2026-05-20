# Tasks: 持久化存储

- [x] 在 `db.py` 的 `_DDL` 中追加 cards 表定义
- [x] 在 `db.py` 中实现 `upsert_card`、`get_card`、`list_cards`、`delete_card`、`toggle_save` 五个函数
- [x] 改写 `store.py` 卡片方法：优先走 db，db 不可用时降级内存
- [x] 验证：重启后端，发起聊天生成卡片，重启后卡片仍存在
