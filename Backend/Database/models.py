from __future__ import annotations
from datetime import UTC, datetime
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from Database.database import Base

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, index=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mode: Mapped[str | None] = mapped_column(String, nullable=True, default="schedule")
    start_time: Mapped[str | None] = mapped_column(String, nullable=True, default="22:00")
    end_time: Mapped[str | None] = mapped_column(String, nullable=True, default="05:00")


class Alert(Base):
    __tablename__ = "alert"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    timestamp: Mapped[str | None] = mapped_column(String, nullable=True)
    alert_type: Mapped[str | None] = mapped_column(String, nullable=True)
    message: Mapped[str | None] = mapped_column(String, nullable=True)
    buzzer_triggered: Mapped[int] = mapped_column(Integer, default=0)
    acknowledged: Mapped[int] = mapped_column(Integer, default=0)
