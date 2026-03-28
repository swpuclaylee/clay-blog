from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_serializer


class TimestampMixin(BaseModel):
    """时间戳混入"""

    created_at: datetime
    updated_at: datetime

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, dt: datetime, _info) -> str:
        """统一序列化时间格式：YYYY-MM-DD HH:MM:SS"""
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class IDMixin(BaseModel):
    """主键混入"""

    id: int


class ORMConfigMixin(BaseModel):
    """ORM 配置混入"""

    model_config = ConfigDict(from_attributes=True)
