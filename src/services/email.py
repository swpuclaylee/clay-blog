import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from src.core.cache.redis_ops import redis_cache
from src.core.config import settings

_EMAIL_CODE_PREFIX = "email_code:"


def _gen_code(length: int = 6) -> str:
    return "".join(random.choices(string.digits, k=length))


async def send_email_code(email: str) -> None:
    """生成验证码写入 Redis，并发送到邮箱"""
    code = _gen_code()
    ttl = settings.EMAIL_CODE_EXPIRE_MINUTES * 60
    await redis_cache.set(f"{_EMAIL_CODE_PREFIX}{email}", code, ex=ttl)

    # 发送邮件（如果未配置 SMTP 则仅记录日志，方便开发环境）
    if not settings.SMTP_USER:
        logger.info(f"[DEV] Email code for {email}: {code}")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "【Clay Blog】邮箱验证码"
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = email

        html_body = f"""
        <div style="font-family:Arial,sans-serif;max-width:480px;margin:0 auto;">
          <h2>邮箱验证码</h2>
          <p>您的验证码为：</p>
          <h1 style="color:#4f46e5;letter-spacing:8px;">{code}</h1>
          <p>验证码 {settings.EMAIL_CODE_EXPIRE_MINUTES} 分钟内有效，请勿泄露。</p>
        </div>
        """
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, [email], msg.as_string())
    except Exception as e:
        logger.error(f"发送验证码邮件失败: {e}")
        raise


async def verify_email_code(email: str, code: str) -> bool:
    """校验验证码（通过后自动删除）"""
    stored = await redis_cache.get(f"{_EMAIL_CODE_PREFIX}{email}")
    if not stored or stored != code:
        return False
    await redis_cache.delete(f"{_EMAIL_CODE_PREFIX}{email}")
    return True
