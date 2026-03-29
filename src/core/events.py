from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from src.core.cache.cache import close_redis, init_redis
from src.db.init_db import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    应用生命周期管理
    """

    # ========== 启动时 ==========
    logger.info("应用启动中...")

    # 1. 初始化数据库连接池
    await init_db()
    logger.info("数据库连接池已初始化")

    # 2. 初始化 Redis 连接
    await init_redis()
    logger.info("Redis 已初始化")

    # 3. 初始化百度内容审核 token
    from src.core.config import settings

    if settings.BDY_API_KEY:
        from src.tasks.review import refresh_bdy_token

        refresh_bdy_token.delay()
        logger.info("百度内容审核 token 初始化任务已派发")

    logger.info("应用启动完成")

    yield

    # ========== 关闭时 ==========

    # 关闭数据库连接池
    await close_db()
    logger.info("数据库连接池已关闭")

    # 关闭 Redis 连接
    await close_redis()
    logger.info("Redis 已关闭")
