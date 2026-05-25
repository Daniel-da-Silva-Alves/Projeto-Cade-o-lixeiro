"""
Cadê o Lixeiro? v2.0 — Serviço de Geocodificação

Cache espacial via PostGIS (raio 50m) + fallback Nominatim.
Ref: RAT-2 SDD §4.2
"""

import logging
from typing import Optional

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
CACHE_RADIUS_METERS = 50


async def geocodificar(
    db: AsyncSession,
    lat: float,
    lng: float,
) -> Optional[str]:
    """
    Geocodifica coordenadas usando cache PostGIS + Nominatim.

    1. Verifica cache (ST_DWithin 50m)
    2. Se cache miss → chama Nominatim
    3. Salva resultado no cache
    """
    # 1. Verificar cache
    cache_result = await db.execute(text("""
        SELECT endereco, cep
        FROM public.cache_geocodificacao
        WHERE ST_DWithin(
            geom,
            ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography,
            :radius
        )
        ORDER BY ST_Distance(
            geom,
            ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography
        )
        LIMIT 1
    """), {"lat": lat, "lng": lng, "radius": CACHE_RADIUS_METERS})

    row = cache_result.first()
    if row:
        return row.endereco

    # 2. Cache miss → chamar Nominatim
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(NOMINATIM_URL, params={
                "lat": lat,
                "lon": lng,
                "format": "json",
                "addressdetails": 1,
                "accept-language": "pt-BR",
            }, headers={
                "User-Agent": "CadeOLixeiro/2.0 (contato@cadeolixeiro.com)",
            })

            if response.status_code != 200:
                logger.warning(f"[Geocode] Nominatim retornou {response.status_code}")
                return None

            data = response.json()
            endereco = data.get("display_name", "")
            address = data.get("address", {})
            cep = address.get("postcode")

            if not endereco:
                return None

            # 3. Salvar no cache
            await db.execute(text("""
                INSERT INTO public.cache_geocodificacao
                    (latitude, longitude, geom, endereco, cep)
                VALUES (
                    :lat, :lng,
                    ST_SetSRID(ST_MakePoint(:lng, :lat), 4326),
                    :endereco, :cep
                )
            """), {"lat": lat, "lng": lng, "endereco": endereco, "cep": cep})
            await db.commit()

            return endereco

    except httpx.TimeoutException:
        logger.warning(f"[Geocode] Timeout Nominatim para ({lat}, {lng})")
        return None
    except Exception as e:
        logger.error(f"[Geocode] Erro: {e}")
        return None


async def geocodificar_e_atualizar(
    caminhao_truck_id: str,
    loc_lat: float,
    loc_lng: float,
):
    """
    Geocodifica e atualiza o endereço no caminhão.
    Executada como asyncio.create_task (não bloqueia o WS loop).
    """
    try:
        from app.database import async_session_factory

        async with async_session_factory() as db:
            endereco = await geocodificar(db, loc_lat, loc_lng)

            if endereco:
                await db.execute(text("""
                    UPDATE public.caminhoes
                    SET ultimo_endereco = :endereco, updated_at = NOW()
                    WHERE truck_id = :tid
                """), {"endereco": endereco, "tid": caminhao_truck_id})
                await db.commit()

                # Atualizar estado no manager
                from app.websockets.manager import manager
                if caminhao_truck_id in manager._estado_caminhoes:
                    manager._estado_caminhoes[caminhao_truck_id]["endereco"] = endereco

    except Exception as e:
        logger.error(f"[Geocode] Erro ao atualizar {caminhao_truck_id}: {e}")
