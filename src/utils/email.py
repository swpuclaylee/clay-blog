import random
import string

from src.core.cache.redis_ops import redis_cache
from src.core.config import settings

_EMAIL_CODE_PREFIX = "email_code:"


def _gen_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


async def send_email_code(email: str) -> None:
    """生成验证码写入 Redis，并通过 Celery 异步发送邮件"""
    code = _gen_code()
    ttl = settings.EMAIL_CODE_EXPIRE_MINUTES * 60
    await redis_cache.set(f"{_EMAIL_CODE_PREFIX}{email}", code, ex=ttl)

    from src.tasks.email import send_email_code as celery_send

    celery_send.delay(email, code)


async def verify_email_code(email: str, code: str) -> bool:
    """校验验证码（通过后自动删除）"""
    stored = await redis_cache.get(f"{_EMAIL_CODE_PREFIX}{email}")
    if not stored or stored != code:
        return False
    await redis_cache.delete(f"{_EMAIL_CODE_PREFIX}{email}")
    return True
