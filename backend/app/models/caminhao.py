"""
Cadê o Lixeiro? v2.0 — Model: Caminhão

Veículos de coleta com status de rastreamento.
Ref: RAT-1 SDD §3.2
"""

import uuid
from datetime import datetime
from sqlalchemy import Text, Float, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

from app.database import Base


class Caminhao(Base):
    __tablename__ = "caminhoes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    truck_id: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    modelo: Mapped[str | None] = mapped_column(Text, nullable=True)
    placa: Mapped[str | None] = mapped_column(Text, nullable=True, unique=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="offline")
    ultima_posicao_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    ultima_posicao_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    ultimo_endereco: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    # Relacionamentos
    motoristas = relationship("Motorista", back_populates="caminhao")
    rotas = relationship("Rota", back_populates="caminhao")
    localizacoes = relationship("LocalizacaoCaminhao", back_populates="caminhao")

    def __repr__(self) -> str:
        return f"<Caminhao(truck_id={self.truck_id!r}, status={self.status!r})>"
