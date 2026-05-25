"""
Cadê o Lixeiro? v2.0 — Model: Motorista

Motorista vinculado a auth.users via Supabase Auth.
Ref: AUT-1 SDD §3.1
"""

import uuid
from datetime import date, datetime
from sqlalchemy import Text, Date, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP, VARCHAR

from app.database import Base


class Motorista(Base):
    __tablename__ = "motoristas"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    auth_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False, unique=True
    )
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    cpf: Mapped[str] = mapped_column(VARCHAR(11), nullable=False, unique=True)
    caminhao_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("caminhoes.id"), nullable=True
    )
    status: Mapped[str] = mapped_column(Text, nullable=False, default="ativo")
    data_nascimento: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    # Relacionamentos
    caminhao = relationship("Caminhao", back_populates="motoristas")

    def __repr__(self) -> str:
        return f"<Motorista(nome={self.nome!r}, cpf={self.cpf!r})>"
