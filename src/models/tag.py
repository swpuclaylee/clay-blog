from sqlalchemy import SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Tag(Base):
    """标签表"""

    __tablename__ = "tag"

    name: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, comment="标签名"
    )
    deleted: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, comment="是否删除：1是 0否"
    )
