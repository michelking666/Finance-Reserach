"""定时任务：每日 17:00 清表，每日 9:00 刷新行情数据。"""
from __future__ import annotations

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.services import db, market

logger = logging.getLogger(__name__)

_scheduler: BackgroundScheduler | None = None


def _job_truncate() -> None:
    logger.info("[scheduler] 17:00 清空所有市场数据表")
    market.clear_cache()
    db.truncate_all()


def _job_refresh() -> None:
    logger.info("[scheduler] 9:00 开始拉取最新行情数据")
    market.refresh_all()


def start() -> None:
    global _scheduler
    _scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
    _scheduler.add_job(_job_truncate, CronTrigger(hour=17, minute=0, timezone="Asia/Shanghai"))
    _scheduler.add_job(_job_refresh, CronTrigger(hour=9, minute=0, timezone="Asia/Shanghai"))
    _scheduler.start()
    logger.info("定时任务已启动（9:00 刷新 / 17:00 清表）")


def shutdown() -> None:
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
