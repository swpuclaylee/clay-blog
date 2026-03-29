"""百度智能云内容审核 token 刷新任务"""
import redis as sync_redis
import requests
from loguru import logger

from src.core.celery_app import celery_app
from src.core.config import settings

_TOKEN_KEY = "bdy_text_review_token"
_TOKEN_URL = "https://aip.baidubce.com/oauth/2.0/token"


def _get_sync_redis():
    return sync_redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        password=settings.REDIS_PASSWORD,
        decode_responses=True,
    )


@celery_app.task(
    name="src.tasks.review.refresh_bdy_token",
    queue="default",
    max_retries=3,
    default_retry_delay=60,
)
def refresh_bdy_token() -> None:
    """刷新百度智能云内容审核 access_token（有效期约30天，每20天刷新一次）"""
    if not settings.BDY_API_KEY:
        return

    try:
        resp = requests.post(
            _TOKEN_URL,
            params={
                "grant_type": "client_credentials",
                "client_id": settings.BDY_API_KEY,
                "client_secret": settings.BDY_SECRET_KEY,
            },
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=10,
        )
        token = resp.json().get("access_token")
        if token:
            r = _get_sync_redis()
            # 存 25 天（提前5天续期）
            r.set(_TOKEN_KEY, token, ex=25 * 24 * 3600)
            logger.info("百度内容审核 token 刷新成功")
        else:
            logger.error(f"百度内容审核 token 刷新失败: {resp.json()}")
    except Exception as e:
        logger.error(f"百度内容审核 token 刷新异常: {e}")
        raise
