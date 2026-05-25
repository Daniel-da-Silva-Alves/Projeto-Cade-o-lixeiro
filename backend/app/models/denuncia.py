"""
Cadê o Lixeiro? v2.0 — Model: Denuncia + TimelineStatus

Sistema de denúncias ambientais anônimas com timeline de status.
Ref: DEN-1 SDD §3.1-3.2
"""

import uuid
from datetime import datetime
from sqlalchemy import Text, Float, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ARRAY

from app.database import Base


class Denuncia(Base):
    __tablename__ = "denuncias"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    id_acompanhamento: Mapped[str] = mapped_column(
        Text, nullable=False, unique=True
    )
    tipo: Mapped[str] = mapped_column(Text, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    bairro_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bairros.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pendente")
    fotos_urls: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list
    )
    ip_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    # Relacionamentos
    bairro = relationship("Bairro", back_populates="denuncias")
    timeline = relationship(
        "TimelineStatus", back_populates="denuncia", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Denuncia(id_acomp={self.id_acompanhamento!r}, status={self.status!r})>"


class TimelineStatus(Base):
    __tablename__ = "timeline_status"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    denuncia_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("denuncias.id", ondelete="CASCADE"),
        nullable=False,
    )
    status_anterior: Mapped[str | None] = mapped_column(Text, nullable=True)
    status_novo: Mapped[str] = mapped_column(Text, nullable=False)
    observacao: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    # Relacionamentos
    denuncia = relationship("Denuncia", back_populates="timeline")

    def __repr__(self) -> str:
        return f"<TimelineStatus(status={self.status_novo!r})>"
