"""
Cadê o Lixeiro? v2.0 — Model: LocalizacaoCaminhao + CacheGeocodificacao

Histórico de posições dos caminhões e cache de geocodificação Nominatim.
Ref: RAT-1 SDD §3.1, RAT-2 SDD §3.1
"""

import uuid
from datetime import datetime
from sqlalchemy import Text, Float, BigInteger, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP
from geoalchemy2 import Geometry

from app.database import Base


class LocalizacaoCaminhao(Base):
    __tablename__ = "localizacoes_caminhao"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    caminhao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("caminhoes.id"), nullable=False
    )
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    endereco: Mapped[str | None] = mapped_column(Text, nullable=True)
    cep: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    # Relacionamentos
    caminhao = relationship("Caminhao", back_populates="localizacoes")

    def __repr__(self) -> str:
        return f"<LocalizacaoCaminhao(caminhao_id={self.caminhao_id}, lat={self.latitude})>"


class CacheGeocodificacao(Base):
    __tablename__ = "cache_geocodificacao"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    geom = mapped_column(Geometry("POINT", srid=4326), nullable=False)
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    bairro_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bairros.id"), nullable=True
    )
    cep: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    def __repr__(self) -> str:
        return f"<CacheGeocodificacao(endereco={self.endereco!r})>"
