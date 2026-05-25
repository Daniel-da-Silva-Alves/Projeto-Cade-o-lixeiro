"""
Cadê o Lixeiro? v2.0 — Model: Rota + PontoRota

Rotas de coleta com pontos de passagem e horários.
Ref: HOR-1 SDD §3.1-3.2
"""

import uuid
from datetime import time, datetime
from sqlalchemy import (
    Text, Float, SmallInteger, Boolean, Time, ForeignKey, text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ARRAY

from app.database import Base


class Rota(Base):
    __tablename__ = "rotas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    caminhao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("caminhoes.id"), nullable=False
    )
    rota_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    bairro_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bairros.id"), nullable=False
    )
    tipo_coleta: Mapped[str] = mapped_column(Text, nullable=False, default="geral")
    dias_semana: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False, default=list
    )
    endereco_inicio: Mapped[str | None] = mapped_column(Text, nullable=True)
    endereco_fim: Mapped[str | None] = mapped_column(Text, nullable=True)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    # Relacionamentos
    caminhao = relationship("Caminhao", back_populates="rotas")
    bairro = relationship("Bairro", back_populates="rotas")
    pontos = relationship("PontoRota", back_populates="rota", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Rota(rota_id={self.rota_id!r}, tipo={self.tipo_coleta!r})>"


class PontoRota(Base):
    __tablename__ = "pontos_rota"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    rota_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("rotas.id", ondelete="CASCADE"), nullable=False
    )
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    cep: Mapped[str | None] = mapped_column(Text, nullable=True)
    ordem: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    horario_passagem: Mapped[time] = mapped_column(Time, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    # Relacionamentos
    rota = relationship("Rota", back_populates="pontos")

    def __repr__(self) -> str:
        return f"<PontoRota(ordem={self.ordem}, endereco={self.endereco!r})>"
