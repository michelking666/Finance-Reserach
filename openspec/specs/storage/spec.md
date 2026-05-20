# Spec: 存储层

## 能力描述

系统维护两类运行时数据：话题卡片（用户生成内容）和技能（静态配置）。

## 当前实现：内存存储

`services/store.py` 用 Python dict + `RLock` 实现线程安全的内存存储。

### 接口契约

```python
# 卡片
store.list_cards(only_saved=False) -> list[TopicCard]
store.get_card(card_id) -> TopicCard | None
store.upsert_card(card) -> TopicCard          # 无 id 时自动生成 uuid4
store.delete_card(card_id) -> bool
store.toggle_save(card_id, saved) -> TopicCard | None

# 技能（只读，启动时从 skills_seed.py 加载）
store.list_skills(q=None, category=None) -> list[Skill]
store.get_skill(skill_id) -> Skill | None
```

### 已知问题

- **重启丢失**：所有卡片在进程重启后消失
- **无持久化**：无法跨会话保留用户收藏
- **单进程**：多 worker 部署时各进程 store 不共享

## 目标实现：PostgreSQL 持久化

见 change: `persistent-storage`。

## 技能的特殊性

技能是静态配置，不需要持久化到数据库：
- 来源：`data/skills_seed.py`（代码即配置）
- 加载时机：`_Store.__init__` 时一次性加载
- 变更方式：修改 `skills_seed.py` 后重启服务
- 不支持运行时增删改

## 市场数据存储

市场数据（热股、债券收益率、基金净值、研报、新闻、公告）存储在 PostgreSQL，由 `services/db.py` 管理：

| 表名 | 内容 | 写入时机 |
|------|------|---------|
| market_hot_stocks | 热门股票行情 | 每次 AKShare 拉取后 |
| market_bond_yields | 中美国债收益率 | 每次 AKShare 拉取后 |
| market_fund_navs | 基金净值 | 每次 AKShare 拉取后 |
| stock_research_reports | 个股卖方研报 | 按需拉取后 |
| stock_news | 个股新闻 | 按需拉取后 |
| fund_announcements | 基金公告 | 按需拉取后 |

市场数据表每日 17:00 清空（`scheduler._job_truncate`），9:00 重新拉取（`scheduler._job_refresh`）。

## 集成点

- `backend/app/services/store.py` — 内存存储实现
- `backend/app/services/db.py` — PostgreSQL 市场数据层
- `backend/app/data/skills_seed.py` — 技能静态配置
- `backend/app/services/scheduler.py` — 市场数据定时清理/刷新
