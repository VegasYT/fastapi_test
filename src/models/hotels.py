from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, UniqueConstraint

from src.database import Base


class HotelsOrm(Base):
    __tablename__ = "hotels"
    __table_args__ = (
        UniqueConstraint("title", "location"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(length=100))
    location: Mapped[str]
