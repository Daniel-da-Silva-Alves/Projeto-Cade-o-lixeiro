"""
Cadê o Lixeiro? v2.0 — Model: Bairro

Bairros de Manaus com geometria PostGIS para resolução espacial.
Ref: DSC-1 SDD §3.3
"""

import uuid
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geometry

from app.database import Base


class Bairro(Base):
    __tablename__ = "bairros"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    geom = mapped_column(Geometry("POLYGON", srid=4326), nullable=True)

    # Relacionamentos
    rotas = relationship("Rota", back_populates="bairro")
    locais_descarte = relationship("LocalDescarte", back_populates="bairro")
    denuncias = relationship("Denuncia", back_populates="bairro")
    subscriptions_push = relationship("SubscriptionPush", back_populates="bairro")

    def __repr__(self) -> str:
        return f"<Bairro(nome={self.nome!r})>"
