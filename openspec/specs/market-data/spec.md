# Spec: 市场数据

## 能力描述

系统通过 AKShare 实时采集 A 股热门行情、中美国债收益率、基金净值，以及按需拉取个股研报、新闻和基金公告，为 LLM 回答提供实时数据支撑。

## 数据来源

所有数据来自 AKShare（需 Python 3.11，其他版本不兼容）。

| 数据类型 | AKShare 接口 | 缓存 TTL |
|---------|-------------|---------|
| 热门股票（东财热门榜） | `stock_hot_rank_em()` | 60s |
| 中美国债收益率 | `bond_zh_us_rate()` | 60s |
| 基金净值（固定观察列表） | `fund_open_fund_info_em()` | 60s |
| 个股卖方研报 | `stock_research_report_em()` | 300s |
| 个股新闻 | `stock_news_em()` | 60s |
| 基金公告 | `fund_announcement_report_em()` | 300s |

## 缓存策略

两级缓存：

1. **内存缓存**（`services/market.py`）：dict + threading.Lock，TTL 60s（行情）或 300s（研报/公告）
2. **PostgreSQL 持久化**（`services/db.py`）：每次 AKShare 拉取后写入，供 LLM 卡片 metrics 查询

AKShare 不可用（ImportError）时静默返回空列表，不抛异常。

## 观察基金列表

固定在 `services/market.py` 中：

```
110020  易方达蓝筹精选  主动权益
000001  华夏成长混合    主动权益
161725  招商中证白酒    指数
003376  中欧纯债债券    纯债
000614  华安中短债      中短债
```

## 定时调度

由 `services/scheduler.py` 管理（APScheduler，Asia/Shanghai 时区）：

| 时间 | 任务 |
|------|------|
| 每日 09:00 | 清空内存缓存 + 重新拉取热股/债券/基金 + 写入 PostgreSQL |
| 每日 17:00 | 清空内存缓存 + 清空所有市场数据表（TRUNCATE） |

## API 接口

```
GET /api/market/snapshot     → { hot_stocks, bond_yields, fund_navs }
GET /api/market/hot-stocks   → list[HotStock]
GET /api/market/bond-yields  → list[BondYield]
GET /api/market/fund-navs    → list[FundNav]
```

## LLM 集成

`llm._fetch_realtime_sources` 按场景决定拉取内容：
- 公司深度/行业研究/事件跟踪：个股研报 + 新闻（需从查询中提取 6 位股票代码）
- 基金研究：基金公告
- 其他场景：不拉取实时来源

`llm._build_card_metrics` 从 PostgreSQL 查询已有数据构建卡片指标，不发起新网络请求。

## 集成点

- `backend/app/services/market.py` — 采集与缓存
- `backend/app/services/db.py` — PostgreSQL 写入与查询
- `backend/app/services/scheduler.py` — 定时任务
- `backend/app/routers/market.py` — HTTP 接口
- `backend/app/services/llm.py` — 实时来源拉取与卡片指标构建
