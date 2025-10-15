import typing
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, String

from src.database import Base

if typing.TYPE_CHECKING:
    from models.rooms import RoomsOrm


class FacilitiesOrm(Base):
    __tablename__ = "facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(length=100), unique=True)

    rooms: Mapped[list["RoomsOrm"]] = relationship(
        back_populates="facilities",
        secondary="rooms_facilities",
        cascade="all, delete"
    )


class RoomsFacilitiesOrm(Base):
    __tablename__ = "rooms_facilities"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"))
    facility_id: Mapped[int] = mapped_column(ForeignKey("facilities.id", ondelete="CASCADE"))
