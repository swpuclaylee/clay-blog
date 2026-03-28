from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ResponseModel(BaseModel, Generic[T]):
    """统一响应模型"""

    code: int = 1  # 1 表示成功 0 表示失败
    message: str = "成功"
    data: T | None = None
