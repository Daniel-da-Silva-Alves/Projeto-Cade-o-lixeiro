"""
Cadê o Lixeiro? v2.0 — Router: Admin Dashboard

Endpoints de KPIs, heatmap de denúncias e estatísticas para dashboard admin.
Ref: ADM-1 SDD §3.1
"""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/api/admin", tags=["admin"])


async def _require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    """Verifica que o usuario é admin (role check simplificado)."""
    # No MVP, qualquer usuario autenticado pode ver o dashboard
    # Em produção, filtrar por user.role == "admin"
    return user


@router.get("/kpis")
async def kpis(
    user: CurrentUser = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Retorna KPIs principais para o dashboard admin."""
    # Caminhões
    cam_result = await db.execute(text("""
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE status = 'online') AS online
        FROM public.caminhoes
    """))
    cam = cam_result.first()

    # Denúncias
    den_result = await db.execute(text("""
        SELECT
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE status = 'pendente') AS pendentes,
            COUNT(*) FILTER (WHERE status = 'em_analise') AS em_analise,
            COUNT(*) FILTER (WHERE status = 'resolvida') AS resolvidas
        FROM public.denuncias
    """))
    den = den_result.first()

    # Rotas ativas
    rotas_result = await db.execute(text(
        "SELECT COUNT(*) AS total FROM public.rotas WHERE ativa = true"
    ))
    rotas = rotas_result.scalar()

    # Locais de descarte
    locais_result = await db.execute(text(
        "SELECT COUNT(*) AS total FROM public.locais_descarte"
    ))
    locais = locais_result.scalar()

    # Motoristas
    mot_result = await db.execute(text(
        "SELECT COUNT(*) AS total FROM public.motoristas WHERE status = 'ativo'"
    ))
    motoristas = mot_result.scalar()

    # Bairros
    bairros_result = await db.execute(text(
        "SELECT COUNT(*) AS total FROM public.bairros"
    ))
    bairros = bairros_result.scalar()

    return {
        "caminhoes": {"total": cam.total, "online": cam.online},
        "denuncias": {
            "total": den.total,
            "pendentes": den.pendentes,
            "em_analise": den.em_analise,
            "resolvidas": den.resolvidas,
        },
        "rotas_ativas": rotas,
        "locais_descarte": locais,
        "motoristas_ativos": motoristas,
        "bairros": bairros,
    }


@router.get("/denuncias-por-status")
async def denuncias_por_status(
    user: CurrentUser = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Dados para gráfico de denúncias agrupadas por status."""
    result = await db.execute(text("""
        SELECT status, COUNT(*) AS total
        FROM public.denuncias
        GROUP BY status
        ORDER BY total DESC
    """))

    return {
        "dados": [
            {"status": row.status, "total": row.total}
            for row in result
        ]
    }


@router.get("/denuncias-heatmap")
async def denuncias_heatmap(
    user: CurrentUser = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Dados de coordenadas de denúncias para mapa de calor."""
    result = await db.execute(text("""
        SELECT latitude, longitude, tipo, status
        FROM public.denuncias
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
        ORDER BY created_at DESC
        LIMIT 500
    """))

    return {
        "pontos": [
            {
                "lat": row.latitude,
                "lng": row.longitude,
                "tipo": row.tipo,
                "status": row.status,
            }
            for row in result
        ]
    }


@router.get("/denuncias-por-bairro")
async def denuncias_por_bairro(
    user: CurrentUser = Depends(_require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Denúncias agrupadas por bairro para gráfico de barras."""
    result = await db.execute(text("""
        SELECT b.nome AS bairro, COUNT(d.id) AS total
        FROM public.denuncias d
        JOIN public.bairros b ON b.id = d.bairro_id
        GROUP BY b.nome
        ORDER BY total DESC
        LIMIT 20
    """))

    return {
        "dados": [
            {"bairro": row.bairro, "total": row.total}
            for row in result
        ]
    }
