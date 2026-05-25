"""
Cadê o Lixeiro? v2.0 — Model: LocalDescarte + AvaliacaoDescarte

Pontos de descarte consciente com avaliações anônimas.
Ref: DSC-1 SDD §3.1-3.2
"""

import uuid
from datetime import datetime
from sqlalchemy import Text, SmallInteger, Float, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, ARRAY, JSONB

from app.database import Base


class LocalDescarte(Base):
    __tablename__ = "locais_descarte"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    endereco: Mapped[str] = mapped_column(Text, nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    bairro_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bairros.id"), nullable=False
    )
    tipos_residuo: Mapped[list[str]] = mapped_column(
        ARRAY(Text), nullable=False
    )
    horarios = mapped_column(JSONB, nullable=True)
    telefone: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    # Relacionamentos
    bairro = relationship("Bairro", back_populates="locais_descarte")
    avaliacoes = relationship(
        "AvaliacaoDescarte", back_populates="local", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<LocalDescarte(nome={self.nome!r})>"


class AvaliacaoDescarte(Base):
    __tablename__ = "avaliacoes_descarte"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    local_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("locais_descarte.id", ondelete="CASCADE"),
        nullable=False,
    )
    estrelas: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    comentario: Mapped[str | None] = mapped_column(Text, nullable=True)
    ip_hash: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    # Relacionamentos
    local = relationship("LocalDescarte", back_populates="avaliacoes")

    def __repr__(self) -> str:
        return f"<AvaliacaoDescarte(estrelas={self.estrelas})>"
