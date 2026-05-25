"""
Cadê o Lixeiro? v2.0 — Router: Denúncias Ambientais

Endpoints para registrar denúncias anônimas e consultar status.
Ref: DEN-1 SDD §4.1
"""

import hashlib
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db

settings = get_settings()
router = APIRouter(prefix="/api/denuncias", tags=["denuncias"])

TIPOS_VALIDOS = {"area_contaminada", "incendio_criminoso", "descarte_ilegal"}
CONTENT_TYPES_VALIDOS = {"image/jpeg", "image/png", "image/webp"}
MAX_FOTOS = 3
MAX_FOTO_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("")
async def criar_denuncia(
    tipo: str = Form(...),
    descricao: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    fotos: list[UploadFile] = File(default=[]),
    request: Request = None,
    db: AsyncSession = Depends(get_db),
):
    """Registra denúncia anônima com fotos e localização."""
    # Validar tipo
    if tipo not in TIPOS_VALIDOS:
        raise HTTPException(400, f"Tipo inválido. Use: {', '.join(TIPOS_VALIDOS)}")

    # Rate limit por IP (max 5 por 24h)
    ip = request.client.host if request and request.client else "unknown"
    ip_hash = hashlib.sha256(ip.encode()).hexdigest()

    contagem = await db.execute(text("""
        SELECT COUNT(*) FROM public.denuncias
        WHERE ip_hash = :ip_hash
          AND created_at > NOW() - INTERVAL '24 hours'
    """), {"ip_hash": ip_hash})

    if (contagem.scalar() or 0) >= 5:
        raise HTTPException(429, "Limite de 5 denúncias por dia atingido.")

    # Validar fotos
    if len(fotos) > MAX_FOTOS:
        raise HTTPException(400, f"Envie no máximo {MAX_FOTOS} fotos.")

    fotos_urls: list[str] = []
    # Upload fotos para Supabase Storage (se houver)
    if fotos:
        try:
            from supabase import create_client
            supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)

            for foto in fotos:
                if foto.content_type not in CONTENT_TYPES_VALIDOS:
                    raise HTTPException(400, f"Formato inválido: {foto.filename}. Use JPG, PNG ou WEBP.")

                conteudo = await foto.read()
                if len(conteudo) > MAX_FOTO_SIZE:
                    raise HTTPException(400, f"{foto.filename} excede 5MB.")

                # Upload path: denuncias/{timestamp}_{filename}
                ts = int(datetime.utcnow().timestamp())
                safe_name = foto.filename.replace(" ", "_") if foto.filename else "foto.jpg"
                path = f"denuncias/{ts}_{safe_name}"

                supabase_client.storage.from_("denuncias").upload(
                    path, conteudo,
                    file_options={"content-type": foto.content_type}
                )
                url = supabase_client.storage.from_("denuncias").get_public_url(path)
                fotos_urls.append(url)
        except ImportError:
            # supabase-py não instalado — skip upload
            pass
        except Exception:
            # Storage error — continue sem fotos
            pass

    # Gerar ID de acompanhamento
    ano = datetime.utcnow().year
    seq = await db.execute(text("SELECT nextval('seq_denuncia_id')"))
    seq_val = seq.scalar()
    id_acomp = f"DEN-{ano}-{seq_val:05d}"

    # Detectar bairro via PostGIS (se geometrias disponíveis)
    bairro_result = await db.execute(text("""
        SELECT id FROM public.bairros
        WHERE geom IS NOT NULL
          AND ST_Contains(geom, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
        LIMIT 1
    """), {"lon": longitude, "lat": latitude})
    bairro_id = bairro_result.scalar_one_or_none()

    # Persistir denúncia
    await db.execute(text("""
        INSERT INTO public.denuncias (
            id_acompanhamento, tipo, descricao,
            latitude, longitude, bairro_id,
            fotos_urls, ip_hash
        ) VALUES (
            :id_acomp, :tipo, :descricao,
            :lat, :lon, :bairro_id,
            :fotos_urls, :ip_hash
        )
    """), {
        "id_acomp": id_acomp,
        "tipo": tipo,
        "descricao": descricao,
        "lat": latitude,
        "lon": longitude,
        "bairro_id": str(bairro_id) if bairro_id else None,
        "fotos_urls": fotos_urls,
        "ip_hash": ip_hash,
    })

    # Timeline inicial
    await db.execute(text("""
        INSERT INTO public.timeline_status (denuncia_id, status_novo)
        SELECT id, 'pendente' FROM public.denuncias
        WHERE id_acompanhamento = :id_acomp
    """), {"id_acomp": id_acomp})

    await db.commit()

    return {"id_acompanhamento": id_acomp, "sucesso": True}


@router.get("/{id_acompanhamento}")
async def consultar_status(
    id_acompanhamento: str,
    db: AsyncSession = Depends(get_db),
):
    """Consulta status de uma denúncia pelo ID de acompanhamento."""
    # Buscar denúncia
    result = await db.execute(text("""
        SELECT
            d.id_acompanhamento, d.tipo, d.descricao,
            d.latitude, d.longitude, d.status,
            d.fotos_urls, d.created_at,
            b.nome AS bairro
        FROM public.denuncias d
        LEFT JOIN public.bairros b ON b.id = d.bairro_id
        WHERE d.id_acompanhamento = :id
    """), {"id": id_acompanhamento.upper()})

    denuncia = result.first()
    if not denuncia:
        raise HTTPException(404, "Denúncia não encontrada.")

    # Buscar timeline
    timeline_result = await db.execute(text("""
        SELECT status_anterior, status_novo, observacao, created_at
        FROM public.timeline_status ts
        JOIN public.denuncias d ON d.id = ts.denuncia_id
        WHERE d.id_acompanhamento = :id
        ORDER BY ts.created_at ASC
    """), {"id": id_acompanhamento.upper()})

    timeline = [
        {
            "status_anterior": row.status_anterior,
            "status_novo": row.status_novo,
            "observacao": row.observacao,
            "data": row.created_at.isoformat() if row.created_at else None,
        }
        for row in timeline_result
    ]

    tipo_labels = {
        "area_contaminada": "Área Contaminada",
        "incendio_criminoso": "Incêndio Criminoso",
        "descarte_ilegal": "Descarte Ilegal",
    }

    status_labels = {
        "pendente": "⏳ Pendente",
        "em_andamento": "🔧 Em Andamento",
        "resolvida": "✅ Resolvida",
        "descartada": "❌ Descartada",
    }

    return {
        "denuncia": {
            "id_acompanhamento": denuncia.id_acompanhamento,
            "tipo": denuncia.tipo,
            "tipo_label": tipo_labels.get(denuncia.tipo, denuncia.tipo),
            "descricao": denuncia.descricao,
            "latitude": denuncia.latitude,
            "longitude": denuncia.longitude,
            "bairro": denuncia.bairro,
            "status": denuncia.status,
            "status_label": status_labels.get(denuncia.status, denuncia.status),
            "fotos_urls": denuncia.fotos_urls or [],
            "data": denuncia.created_at.isoformat() if denuncia.created_at else None,
        },
        "timeline": timeline,
    }
