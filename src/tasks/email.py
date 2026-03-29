import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from loguru import logger

from src.core.celery_app import celery_app
from src.core.config import settings


@celery_app.task(
    bind=True,
    name="src.tasks.email.send_email_code",
    queue="email",
    max_retries=3,
    default_retry_delay=5,
)
def send_email_code(self, email: str, code: str) -> None:
    """
    Celery 任务：发送邮箱验证码

    Args:
        email: 收件人邮箱
        code:  验证码
    """
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

        logger.info(f"验证码邮件发送成功: {email}")

    except Exception as exc:
        logger.error(f"发送验证码邮件失败 ({email}): {exc}")
        raise self.retry(exc=exc) from exc
