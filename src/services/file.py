from datetime import datetime

from fastapi import UploadFile, HTTPException, status

from src.core.config import settings
from src.utils.minio_client import minio_client

# 允许的图片类型
_ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
# 最大 10MB
_MAX_SIZE = 10 * 1024 * 1024


async def upload_image(file: UploadFile) -> str:
    """
    上传图片到 MinIO，返回可直接访问的预签名 URL（7天有效）

    Args:
        file: FastAPI UploadFile

    Returns:
        预签名 URL 字符串
    """
    if file.content_type not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片类型：{file.content_type}，允许：{', '.join(_ALLOWED_TYPES)}",
        )

    content = await file.read()
    if len(content) > _MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="图片大小不能超过 10MB",
        )

    # 按日期组织目录：images/2024/01/filename_timestamp.ext
    now = datetime.now()
    folder = f"images/{now.year}/{now.month:02d}"

    result = minio_client.upload_bytes(
        data=content,
        filename=file.filename or "upload",
        folder=folder,
        content_type=file.content_type,
    )

    if not result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败：{result.get('error', '未知错误')}",
        )

    # 生成图片预签名 URL（内联显示，不强制下载）
    url = minio_client.get_presigned_url(
        object_name=result["object_name"],
        expires=7,
        force_download=False,
    )

    if not url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="生成图片访问链接失败",
        )

    return url
