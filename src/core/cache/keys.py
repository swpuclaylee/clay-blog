from src.core.config import settings


def make_cache_key(*parts: str) -> str:
    """
    生成格式化的 Redis key

    示例:
        make_cache_key("user", "info", "123") -> "fastapi:user:info:123"
    """
    return f"{settings.PROJECT_NAME.lower()}:{':'.join(parts)}"


class CacheTTL:
    """缓存过期时间配置（秒）"""

    UPLOAD_SESSION = 3600  # 1小时


class CacheKey:
    """Redis 缓存 Key 管理"""

    @staticmethod
    def upload_session(upload_id: str) -> str:
        """
        上传会话 Key

        格式: {project}:upload:session:{upload_id}
        示例: fastapi:upload:session:abc-123
        """
        return make_cache_key("upload", "session", upload_id)
