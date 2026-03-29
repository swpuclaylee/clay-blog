"""
初始化数据脚本

功能：
1. 创建 admin 账号（如不存在）
2. 上传默认头像到 MinIO（static/images/avatar/）

执行方式：
    python -m src.init_data

docker-compose 中可在 backend 启动后通过 command 调用：
    alembic upgrade head && python -m src.init_data && gunicorn ...
"""

import asyncio
import io
import os

from loguru import logger
from sqlalchemy import select

from src.core.config import PROJECT_ROOT, settings
from src.core.security import get_password_hash
from src.db.session import db_manager
from src.models.user import User

# 默认 admin 账号配置（可通过环境变量覆盖）
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@clayblog.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@2025")
ADMIN_NICKNAME = os.getenv("ADMIN_NICKNAME", "Admin")

# MinIO 头像存储路径
AVATAR_BUCKET = settings.MINIO_BUCKET
AVATAR_PREFIX = "static/images/avatar"

# 本地默认头像目录（项目根目录下的 static/images/avatar/）
LOCAL_AVATAR_DIR = PROJECT_ROOT / "static" / "images" / "avatar"


def _upload_avatars_to_minio() -> dict[str, str]:
    """将本地默认头像上传到 MinIO，返回 {filename: minio_path}"""
    from src.utils.minio_client import MinioClient

    client = MinioClient()
    client.ensure_bucket(AVATAR_BUCKET)

    uploaded: dict[str, str] = {}

    if not LOCAL_AVATAR_DIR.exists():
        logger.warning(f"本地头像目录不存在，跳过上传: {LOCAL_AVATAR_DIR}")
        return uploaded

    for avatar_file in LOCAL_AVATAR_DIR.glob("*"):
        if not avatar_file.is_file():
            continue
        object_name = f"{AVATAR_PREFIX}/{avatar_file.name}"
        try:
            with open(avatar_file, "rb") as f:
                data = f.read()
            client.client.put_object(
                bucket_name=AVATAR_BUCKET,
                object_name=object_name,
                data=io.BytesIO(data),
                length=len(data),
                content_type=_guess_content_type(avatar_file.suffix),
            )
            uploaded[avatar_file.name] = object_name
            logger.info(f"上传头像: {object_name}")
        except Exception as e:
            logger.warning(f"上传头像失败 {avatar_file.name}: {e}")

    return uploaded


def _guess_content_type(suffix: str) -> str:
    mapping = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
    }
    return mapping.get(suffix.lower(), "application/octet-stream")


def _default_avatar_path() -> str:
    """返回默认头像 MinIO 路径"""
    return f"{AVATAR_PREFIX}/default.png"


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
        avatar=_default_avatar_path(),
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

    # 2. 上传默认头像到 MinIO
    try:
        uploaded = _upload_avatars_to_minio()
        logger.info(f"共上传 {len(uploaded)} 个头像文件")
    except Exception as e:
        logger.warning(f"MinIO 头像上传失败（可能服务未就绪）: {e}")

    # 3. 创建 admin 账号
    async with db_manager.get_session() as db:
        await create_admin_user(db)

    await db_manager.close()
    logger.info("初始化数据完成")


if __name__ == "__main__":
    asyncio.run(main())
