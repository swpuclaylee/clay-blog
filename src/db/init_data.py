"""
初始化数据脚本

功能：
1. 创建 admin 账号（如不存在）

执行方式：
    python -m src.init_data

docker-compose 中可在 backend 启动后通过 command 调用：
    alembic upgrade head && python -m src.init_data && gunicorn ...
"""

import asyncio
import os

from loguru import logger
from sqlalchemy import select

from src.core.config import settings
from src.core.security import get_password_hash
from src.db.session import db_manager
from src.models.user import User

# 默认 admin 账号配置（可通过环境变量覆盖）
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@clayblog.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@2025")
ADMIN_NICKNAME = os.getenv("ADMIN_NICKNAME", "Admin")


async def create_admin_user(db) -> None:
    """创建 admin 账号（如已存在则跳过）"""

    result = await db.execute(select(User).where(User.email == ADMIN_EMAIL))
    existing = result.scalar_one_or_none()
    if existing:
        logger.info(f"Admin 账号已存在: {ADMIN_EMAIL}")
        return

    admin = User(
        username="admin",
        email=ADMIN_EMAIL,
        password=get_password_hash(ADMIN_PASSWORD),
        nickname=ADMIN_NICKNAME,
        admin=1,
        status=0,
    )
    db.add(admin)
    await db.commit()
    logger.info(f"Admin 账号已创建: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")


async def main() -> None:
    logger.info("开始初始化数据...")

    # 1. 初始化数据库连接
    db_manager.init(
        database_url=settings.DATABASE_URL,
        echo=False,
        pool_size=2,
        max_overflow=2,
    )

    # 3. 创建 admin 账号
    async with db_manager.get_session() as db:
        await create_admin_user(db)

    await db_manager.close()
    logger.info("初始化数据完成")


if __name__ == "__main__":
    asyncio.run(main())
