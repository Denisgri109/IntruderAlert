from __future__ import annotations
from datetime import UTC, datetime
from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
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

    devices: Mapped[list[Device]] = relationship(
        back_populates="user"
    )


class Device(Base):
    __tablename__ = "device"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=False, index=True)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    device_code: Mapped[str | None] = mapped_column(String, unique=True, index=True, nullable=True)
    mode: Mapped[str | None] = mapped_column(String, nullable=True, default="schedule")
    is_online: Mapped[int] = mapped_column(Integer, default=0)
    last_seen: Mapped[str | None] = mapped_column(String, nullable=True)

    user: Mapped[User] = relationship(back_populates="devices")
    schedules: Mapped[list[Schedule]] = relationship(
        back_populates="device",
    )
    alerts: Mapped[list[Alert]] = relationship(
        back_populates="device",
    )


class Schedule(Base):
    __tablename__ = "schedule"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"), nullable=False, index=True)
    start_time: Mapped[str | None] = mapped_column(String, nullable=True, default="22:00")
    end_time: Mapped[str | None] = mapped_column(String, nullable=True, default="05:00")

    device: Mapped[Device] = relationship(back_populates="schedules")


class Alert(Base):
    __tablename__ = "alert"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("device.id"), nullable=False, index=True)
    timestamp: Mapped[str | None] = mapped_column(String, nullable=True)
    alert_type: Mapped[str | None] = mapped_column(String, nullable=True)
    message: Mapped[str | None] = mapped_column(String, nullable=True)
    buzzer_triggered: Mapped[int] = mapped_column(Integer, default=0)
    acknowledged: Mapped[int] = mapped_column(Integer, default=0)

    device: Mapped[Device] = relationship(back_populates="alerts")
