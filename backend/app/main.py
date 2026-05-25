"""
Cadê o Lixeiro? v2.0 — FastAPI Application

Ponto de entrada da API. Configura CORS, routers, WebSocket endpoints e SQLAdmin.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle hooks — startup e shutdown."""
    # Startup
    print(f"[START] {settings.APP_NAME} v{settings.APP_VERSION} iniciando...")

    # Iniciar scheduler para refresh da MV ranking (6.4)
    from app.services.scheduler import iniciar_scheduler
    iniciar_scheduler()

    yield
    # Shutdown
    print(f"[STOP] {settings.APP_NAME} encerrando...")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API de rastreamento de caminhões de coleta — Manaus/AM",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Health Check ---
@app.get("/health", tags=["system"])
async def health():
    """Endpoint de saúde para verificação de disponibilidade."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


# --- Routers ---
from app.routers import bairros, auth, ranking, descarte, rotas, denuncias, notificacoes, admin

app.include_router(bairros.router)
app.include_router(auth.router)
app.include_router(ranking.router)
app.include_router(descarte.router)
app.include_router(rotas.router)
app.include_router(denuncias.router)
app.include_router(notificacoes.router)
app.include_router(admin.router)

# --- WebSocket Endpoints ---
from app.websockets import tracking_hub, driver_hub

app.include_router(tracking_hub.router)
app.include_router(driver_hub.router)

# --- SQLAdmin (CRUD) ---
try:
    from app.admin.setup import setup_admin
    from app.database import engine
    setup_admin(app, engine)
except Exception as e:
    print(f"[WARN] SQLAdmin não inicializado: {e}")
