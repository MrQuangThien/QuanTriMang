from datetime import datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BackupRecord(Base):
    __tablename__ = "backups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device: Mapped[str] = mapped_column(String(100), index=True)
    path: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(30))
    changed: Mapped[str] = mapped_column(String(10), default="UNKNOWN")
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        index=True,
    )
