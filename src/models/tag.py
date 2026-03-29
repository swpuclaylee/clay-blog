from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class Tag(Base):
    """标签表"""

    __tablename__ = "tag"

    name: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, comment="标签名"
    )
