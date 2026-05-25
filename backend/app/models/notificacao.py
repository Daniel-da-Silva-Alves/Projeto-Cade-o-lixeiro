"""
Cadê o Lixeiro? v2.0 — Model: SubscriptionPush + LogNotificacao

Subscriptions Web Push (VAPID) e log anti-spam de notificações.
Ref: NOT-1 SDD §3.1-3.2
"""

import uuid
from datetime import datetime
from sqlalchemy import Text, ForeignKey, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, TIMESTAMP

from app.database import Base


class SubscriptionPush(Base):
    __tablename__ = "subscriptions_push"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    bairro_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bairros.id"), nullable=False
    )
    endpoint: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    p256dh: Mapped[str] = mapped_column(Text, nullable=False)
    auth_key: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    # Relacionamentos
    bairro = relationship("Bairro", back_populates="subscriptions_push")

    def __repr__(self) -> str:
        return f"<SubscriptionPush(bairro_id={self.bairro_id})>"


class LogNotificacao(Base):
    __tablename__ = "log_notificacoes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    bairro_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    caminhao_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )
    enviado_em: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()")
    )

    def __repr__(self) -> str:
        return f"<LogNotificacao(bairro={self.bairro_id}, caminhao={self.caminhao_id})>"
