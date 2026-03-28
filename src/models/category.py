from sqlalchemy import Integer, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Category(Base):
    """分类表"""

    __tablename__ = "category"

    name: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, comment="分类名"
    )
    description: Mapped[str | None] = mapped_column(
        String(256), nullable=True, comment="描述"
    )
    parent_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="父分类ID"
    )
    deleted: Mapped[int] = mapped_column(
        SmallInteger, nullable=False, default=0, comment="是否删除：1是 0否"
    )
