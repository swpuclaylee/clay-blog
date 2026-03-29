from fastapi import APIRouter, Depends, File, UploadFile

from src.api.deps import get_current_user
from src.models.user import User
from src.schemas.base import ResponseModel
from src.utils.file import upload_image

router = APIRouter(prefix="/file", tags=["文件上传"])


@router.post(
    "/upload",
    response_model=ResponseModel[str],
    summary="上传图片",
)
async def upload_file(
    file: UploadFile = File(...),
    _: User = Depends(get_current_user),
):
    """
    上传图片到 MinIO，返回 7 天有效的预签名 URL。

    - 支持格式：JPEG / PNG / GIF / WebP
    - 最大大小：10 MB
    - 返回 data 为图片访问 URL 字符串，可直接填入封面、头像等字段
    """
    url = await upload_image(file)
    return ResponseModel(data=url, message="上传成功")
