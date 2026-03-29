"""百度智能云内容审核工具函数"""
import base64

import httpx
from loguru import logger

from src.core.cache.redis_ops import redis_cache
from src.core.config import settings

_TOKEN_KEY = "bdy_text_review_token"
_TEXT_REVIEW_URL = (
    "https://aip.baidubce.com/rest/2.0/solution/v1/text_censor/v2/user_defined"
)
_IMG_REVIEW_URL = (
    "https://aip.baidubce.com/rest/2.0/solution/v1/img_censor/v2/user_defined"
)


def _is_configured() -> bool:
    return bool(settings.BDY_API_KEY and settings.BDY_SECRET_KEY)


async def _get_token() -> str | None:
    return await redis_cache.get(_TOKEN_KEY)


async def text_review(text: str) -> bool:
    """
    文本审核。返回 True 表示内容合规，False 表示违规。
    未配置百度密钥时直接放行。
    """
    if not _is_configured():
        return True

    token = await _get_token()
    if not token:
        logger.warning("百度内容审核 token 未初始化，跳过文本审核")
        return True
    data = {
        'text': text,
        'strategyId': 1
    }
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.post(
                _TEXT_REVIEW_URL,
                params={"access_token": token},
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                data=data,
            )
            result = resp.json()
            if "error_code" in result:
                logger.error(f"文本审核请求失败: {result.get('error_msg')}")
                return False
            conclusion = result.get("conclusion")
            if conclusion != "合规":
                logger.warning(f"文本审核不合规: conclusion={conclusion}, text={text[:50]}")
                return False
            return True
    except Exception as e:
        logger.error(f"文本审核请求失败: {e}")
        return True  # 审核接口异常时放行，避免影响正常使用


async def image_review(image_bytes: bytes) -> bool:
    """
    图片审核。返回 True 表示图片合规，False 表示违规。
    未配置百度密钥时直接放行。
    """
    if not _is_configured():
        return True

    token = await _get_token()
    if not token:
        logger.warning("百度内容审核 token 未初始化，跳过图片审核")
        return True

    try:
        img_b64 = base64.b64encode(image_bytes).decode()
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(
                f"{_IMG_REVIEW_URL}?access_token={token}",
                headers={"content-type": "application/x-www-form-urlencoded"},
                data={"image": img_b64},
            )
            result = resp.json()
            conclusion = result.get("conclusion", "合规")
            if conclusion != "合规":
                logger.warning(f"图片审核不合规: conclusion={conclusion}")
                return False
            return True
    except Exception as e:
        logger.error(f"图片审核请求失败: {e}")
        return True
