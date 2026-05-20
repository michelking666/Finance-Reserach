"""PostgreSQL 持久化层：连接池、建表、写入函数。"""
from __future__ import annotations

import json
import os
import logging
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2 import pool as pg_pool
from psycopg2.extras import execute_values

logger = logging.getLogger(__name__)

_pool: pg_pool.ThreadedConnectionPool | None = None

_DDL = """
CREATE TABLE IF NOT EXISTS market_hot_stocks (
    id          SERIAL PRIMARY KEY,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    code        TEXT NOT NULL,
    name        TEXT NOT NULL,
    price       TEXT,
    change      TEXT,
    up          BOOLEAN
);

CREATE TABLE IF NOT EXISTS market_bond_yields (
    id          SERIAL PRIMARY KEY,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    code        TEXT NOT NULL,
    name        TEXT NOT NULL,
    price       TEXT,
    yield_      TEXT,
    change      TEXT
);

CREATE TABLE IF NOT EXISTS market_fund_navs (
    id          SERIAL PRIMARY KEY,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    code        TEXT NOT NULL,
    name        TEXT NOT NULL,
    nav         TEXT,
    change      TEXT,
    fund_type   TEXT,
    up          BOOLEAN
);

CREATE TABLE IF NOT EXISTS stock_research_reports (
    id           SERIAL PRIMARY KEY,
    fetched_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    symbol       TEXT NOT NULL,
    title        TEXT,
    institution  TEXT,
    rating       TEXT,
    report_date  TEXT,
    url          TEXT,
    eps_forecast TEXT
);

CREATE TABLE IF NOT EXISTS stock_news (
    id          SERIAL PRIMARY KEY,
    fetched_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    symbol      TEXT NOT NULL,
    title       TEXT,
    content     TEXT,
    news_date   TEXT,
    source      TEXT,
    url         TEXT
);

CREATE TABLE IF NOT EXISTS fund_announcements (
    id           SERIAL PRIMARY KEY,
    fetched_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    symbol       TEXT NOT NULL,
    title        TEXT,
    ann_type     TEXT,
    ann_date     TEXT,
    url          TEXT
);

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

CREATE TABLE IF NOT EXISTS users (
    id               SERIAL PRIMARY KEY,
    username         TEXT NOT NULL UNIQUE,
    hashed_password  TEXT NOT NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active        BOOLEAN NOT NULL DEFAULT TRUE
);
"""


def init() -> None:
    global _pool
    url = os.environ.get("DATABASE_URL")
    if not url:
        logger.warning("DATABASE_URL 未设置，跳过数据库初始化")
        return
    try:
        _pool = pg_pool.ThreadedConnectionPool(minconn=1, maxconn=5, dsn=url)
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(_DDL)
            conn.commit()
        logger.info("数据库初始化完成")
    except Exception as exc:
        logger.error("数据库初始化失败: %s", exc)
        _pool = None


@contextmanager
def _conn() -> Generator:
    if _pool is None:
        raise RuntimeError("数据库连接池未初始化")
    conn = _pool.getconn()
    try:
        yield conn
    finally:
        _pool.putconn(conn)


def _available() -> bool:
    return _pool is not None


# ── 写入函数 ──────────────────────────────────────────────

def save_hot_stocks(rows: list[dict]) -> None:
    if not _available() or not rows:
        return
    try:
        with _conn() as conn, conn.cursor() as cur:
            execute_values(
                cur,
                "INSERT INTO market_hot_stocks (code, name, price, change, up) VALUES %s",
                [(r["code"], r["name"], r.get("price"), r.get("change"), r.get("up")) for r in rows],
            )
            conn.commit()
    except Exception as exc:
        logger.error("save_hot_stocks 失败: %s", exc)


def save_bond_yields(rows: list[dict]) -> None:
    if not _available() or not rows:
        return
    try:
        with _conn() as conn, conn.cursor() as cur:
            execute_values(
                cur,
                "INSERT INTO market_bond_yields (code, name, price, yield_, change) VALUES %s",
                [(r["code"], r["name"], r.get("price"), r.get("yield_"), r.get("change")) for r in rows],
            )
            conn.commit()
    except Exception as exc:
        logger.error("save_bond_yields 失败: %s", exc)


def save_fund_navs(rows: list[dict]) -> None:
    if not _available() or not rows:
        return
    try:
        with _conn() as conn, conn.cursor() as cur:
            execute_values(
                cur,
                "INSERT INTO market_fund_navs (code, name, nav, change, fund_type, up) VALUES %s",
                [(r["code"], r["name"], r.get("nav"), r.get("change"), r.get("type"), r.get("up")) for r in rows],
            )
            conn.commit()
    except Exception as exc:
        logger.error("save_fund_navs 失败: %s", exc)


def save_stock_research_reports(symbol: str, rows: list[dict]) -> None:
    if not _available() or not rows:
        return
    try:
        with _conn() as conn, conn.cursor() as cur:
            execute_values(
                cur,
                """INSERT INTO stock_research_reports
                   (symbol, title, institution, rating, report_date, url, eps_forecast) VALUES %s""",
                [(symbol, r.get("title"), r.get("institution"), r.get("rating"),
                  r.get("date"), r.get("url"), r.get("eps_forecast")) for r in rows],
            )
            conn.commit()
    except Exception as exc:
        logger.error("save_stock_research_reports 失败: %s", exc)


def save_stock_news(symbol: str, rows: list[dict]) -> None:
    if not _available() or not rows:
        return
    try:
        with _conn() as conn, conn.cursor() as cur:
            execute_values(
                cur,
                """INSERT INTO stock_news
                   (symbol, title, content, news_date, source, url) VALUES %s""",
                [(symbol, r.get("title"), r.get("content"), r.get("date"),
                  r.get("source"), r.get("url")) for r in rows],
            )
            conn.commit()
    except Exception as exc:
        logger.error("save_stock_news 失败: %s", exc)


def save_fund_announcements(symbol: str, rows: list[dict]) -> None:
    if not _available() or not rows:
        return
    try:
        with _conn() as conn, conn.cursor() as cur:
            execute_values(
                cur,
                """INSERT INTO fund_announcements
                   (symbol, title, ann_type, ann_date, url) VALUES %s""",
                [(symbol, r.get("title"), r.get("type"), r.get("date"), r.get("url")) for r in rows],
            )
            conn.commit()
    except Exception as exc:
        logger.error("save_fund_announcements 失败: %s", exc)


def query_stock_by_name(name: str) -> dict | None:
    """按股票名称模糊查最新一条行情记录。"""
    if not _available():
        return None
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT code, name, price, change, up FROM market_hot_stocks "
                "WHERE name ILIKE %s ORDER BY fetched_at DESC LIMIT 1",
                (f"%{name}%",),
            )
            row = cur.fetchone()
            if row:
                return {"code": row[0], "name": row[1], "price": row[2], "change": row[3], "up": row[4]}
    except Exception as exc:
        logger.error("query_stock_by_name 失败: %s", exc)
    return None


def query_fund_by_name(name: str) -> dict | None:
    """按基金名称模糊查最新一条净值记录。"""
    if not _available():
        return None
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT code, name, nav, change, fund_type FROM market_fund_navs "
                "WHERE name ILIKE %s ORDER BY fetched_at DESC LIMIT 1",
                (f"%{name}%",),
            )
            row = cur.fetchone()
            if row:
                return {"code": row[0], "name": row[1], "nav": row[2], "change": row[3], "type": row[4]}
    except Exception as exc:
        logger.error("query_fund_by_name 失败: %s", exc)
    return None


def query_bond_by_name(name: str) -> dict | None:
    """按债券名称模糊查最新一条收益率记录。"""
    if not _available():
        return None
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT code, name, price, yield_, change FROM market_bond_yields "
                "WHERE name ILIKE %s ORDER BY fetched_at DESC LIMIT 1",
                (f"%{name}%",),
            )
            row = cur.fetchone()
            if row:
                return {"code": row[0], "name": row[1], "price": row[2], "yield_": row[3], "change": row[4]}
    except Exception as exc:
        logger.error("query_bond_by_name 失败: %s", exc)
    return None


def query_stock_reports(symbol: str, top_n: int = 3) -> list[dict]:
    """查某股票最新研报。"""
    if not _available():
        return []
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT title, institution, rating, report_date, url, eps_forecast "
                "FROM stock_research_reports WHERE symbol = %s "
                "ORDER BY fetched_at DESC LIMIT %s",
                (symbol, top_n),
            )
            return [
                {"title": r[0], "institution": r[1], "rating": r[2],
                 "date": r[3], "url": r[4], "eps_forecast": r[5]}
                for r in cur.fetchall()
            ]
    except Exception as exc:
        logger.error("query_stock_reports 失败: %s", exc)
    return []


def query_latest_hot_stocks(top_n: int = 3) -> list[dict]:
    """查最新热门股票（取最近一批）。"""
    if not _available():
        return []
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT ON (code) code, name, price, change, up "
                "FROM market_hot_stocks ORDER BY code, fetched_at DESC LIMIT %s",
                (top_n,),
            )
            return [
                {"code": r[0], "name": r[1], "price": r[2], "change": r[3], "up": r[4]}
                for r in cur.fetchall()
            ]
    except Exception as exc:
        logger.error("query_latest_hot_stocks 失败: %s", exc)
    return []


def query_latest_bond_yields() -> list[dict]:
    """查最新债券收益率。"""
    if not _available():
        return []
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT ON (code) code, name, price, yield_, change "
                "FROM market_bond_yields ORDER BY code, fetched_at DESC LIMIT 3",
            )
            return [
                {"code": r[0], "name": r[1], "price": r[2], "yield_": r[3], "change": r[4]}
                for r in cur.fetchall()
            ]
    except Exception as exc:
        logger.error("query_latest_bond_yields 失败: %s", exc)
    return []


def query_latest_fund_navs(top_n: int = 3) -> list[dict]:
    """查最新基金净值。"""
    if not _available():
        return []
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT ON (code) code, name, nav, change, fund_type "
                "FROM market_fund_navs ORDER BY code, fetched_at DESC LIMIT %s",
                (top_n,),
            )
            return [
                {"code": r[0], "name": r[1], "nav": r[2], "change": r[3], "type": r[4]}
                for r in cur.fetchall()
            ]
    except Exception as exc:
        logger.error("query_latest_fund_navs 失败: %s", exc)
    return []


_ALL_TABLES = [
    "market_bond_yields",
    "market_fund_navs",
    "stock_research_reports",
    "stock_news",
    "fund_announcements",
]


def truncate_all() -> None:
    if not _available():
        return
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(f"TRUNCATE {', '.join(_ALL_TABLES)} RESTART IDENTITY")
            conn.commit()
        logger.info("所有市场数据表已清空")
    except Exception as exc:
        logger.error("truncate_all 失败: %s", exc)


# ── 卡片 CRUD ─────────────────────────────────────────────

def upsert_card(card: dict) -> None:
    if not _available():
        return
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO cards (id, title, subtitle, summary, tags, metrics, bullets, scenario, sources, created_at, saved)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    title = EXCLUDED.title,
                    subtitle = EXCLUDED.subtitle,
                    summary = EXCLUDED.summary,
                    tags = EXCLUDED.tags,
                    metrics = EXCLUDED.metrics,
                    bullets = EXCLUDED.bullets,
                    scenario = EXCLUDED.scenario,
                    sources = EXCLUDED.sources,
                    saved = EXCLUDED.saved
                """,
                (
                    card["id"], card["title"], card.get("subtitle"), card["summary"],
                    json.dumps(card.get("tags", []), ensure_ascii=False),
                    json.dumps(card.get("metrics", []), ensure_ascii=False),
                    json.dumps(card.get("bullets", []), ensure_ascii=False),
                    card.get("scenario"),
                    json.dumps(card.get("sources", []), ensure_ascii=False),
                    card.get("created_at"),
                    card.get("saved", False),
                ),
            )
            conn.commit()
    except Exception as exc:
        logger.error("upsert_card 失败: %s", exc)


def get_card(card_id: str) -> dict | None:
    if not _available():
        return None
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT id, title, subtitle, summary, tags, metrics, bullets, scenario, sources, created_at, saved "
                "FROM cards WHERE id = %s",
                (card_id,),
            )
            row = cur.fetchone()
            if row:
                return _row_to_card(row)
    except Exception as exc:
        logger.error("get_card 失败: %s", exc)
    return None


def list_cards(only_saved: bool = False) -> list[dict]:
    if not _available():
        return []
    try:
        with _conn() as conn, conn.cursor() as cur:
            if only_saved:
                cur.execute(
                    "SELECT id, title, subtitle, summary, tags, metrics, bullets, scenario, sources, created_at, saved "
                    "FROM cards WHERE saved = TRUE ORDER BY created_at DESC"
                )
            else:
                cur.execute(
                    "SELECT id, title, subtitle, summary, tags, metrics, bullets, scenario, sources, created_at, saved "
                    "FROM cards ORDER BY created_at DESC"
                )
            return [_row_to_card(row) for row in cur.fetchall()]
    except Exception as exc:
        logger.error("list_cards 失败: %s", exc)
    return []


def delete_card(card_id: str) -> bool:
    if not _available():
        return False
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute("DELETE FROM cards WHERE id = %s", (card_id,))
            conn.commit()
            return cur.rowcount > 0
    except Exception as exc:
        logger.error("delete_card 失败: %s", exc)
    return False


def toggle_save(card_id: str, saved: bool) -> dict | None:
    if not _available():
        return None
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "UPDATE cards SET saved = %s WHERE id = %s "
                "RETURNING id, title, subtitle, summary, tags, metrics, bullets, scenario, sources, created_at, saved",
                (saved, card_id),
            )
            conn.commit()
            row = cur.fetchone()
            if row:
                return _row_to_card(row)
    except Exception as exc:
        logger.error("toggle_save 失败: %s", exc)
    return None


def _row_to_card(row: tuple) -> dict:
    return {
        "id": row[0],
        "title": row[1],
        "subtitle": row[2],
        "summary": row[3],
        "tags": row[4] if isinstance(row[4], list) else json.loads(row[4] or "[]"),
        "metrics": row[5] if isinstance(row[5], list) else json.loads(row[5] or "[]"),
        "bullets": row[6] if isinstance(row[6], list) else json.loads(row[6] or "[]"),
        "scenario": row[7],
        "sources": row[8] if isinstance(row[8], list) else json.loads(row[8] or "[]"),
        "created_at": row[9].isoformat() if hasattr(row[9], "isoformat") else str(row[9]),
        "saved": row[10],
    }


# ── 用户 CRUD ─────────────────────────────────────────────

def get_user_by_username(username: str) -> dict | None:
    if not _available():
        return None
    try:
        with _conn() as conn, conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, hashed_password, is_active FROM users WHERE username = %s",
                (username,),
            )
            row = cur.fetchone()
            if row:
                return {"id": row[0], "username": row[1], "hashed_password": row[2], "is_active": row[3]}
    except Exception as exc:
        logger.error("get_user_by_username 失败: %s", exc)
    return None


def create_user(username: str, hashed_password: str) -> dict:
    with _conn() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (username, hashed_password) VALUES (%s, %s) RETURNING id, username, is_active",
            (username, hashed_password),
        )
        conn.commit()
        row = cur.fetchone()
        return {"id": row[0], "username": row[1], "is_active": row[2]}

