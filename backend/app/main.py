"""FastAPI application entry point with lifespan management."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .database import init_db
from .auth.router import router as auth_router
from .prediction.router import router as prediction_router
from .prediction.service import load_model, is_model_loaded, get_class_names

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle management."""
    # ── Startup ──
    logger.info("Starting DermAI API...")
    init_db()
    model_loaded = load_model()
    if model_loaded:
        logger.info("✅ Application ready — model loaded")
    else:
        logger.warning("⚠️ Application started WITHOUT model — predictions will fail")
    yield
    # ── Shutdown ──
    logger.info("Shutting down...")


app = FastAPI(
    title="DermAI API",
    description="AI-powered skin condition screening with educational health insights",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──
app.include_router(auth_router)
app.include_router(prediction_router)


@app.get("/", tags=["Health"])
async def root():
    return {"status": "ok", "message": "DermAI API v1.0"}


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint — verifies model and DB status."""
    from .database import get_db

    db_ok = False
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
            db_ok = True
    except Exception:
        pass

    return {
        "status": "healthy" if (is_model_loaded() and db_ok) else "degraded",
        "model_loaded": is_model_loaded(),
        "database_connected": db_ok,
        "environment": settings.ENVIRONMENT,
        "classes": get_class_names(),
    }
