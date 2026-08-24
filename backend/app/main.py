"""
FastAPI application entry point.

Responsible for:
  - App instantiation
  - CORS middleware
  - Lifespan: load ML model on startup
  - Router registration
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.core.config import get_settings
from app.services import sentiment_service

# ── Logging ───────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


# ── Lifespan (startup / shutdown) ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: load the DistilBERT sentiment model so it is ready for requests.
    The model is loaded once and reused for the application lifetime.
    """
    logger.info("Starting %s v%s", settings.app_name, settings.app_version)
    sentiment_service.load_model()
    logger.info("Application startup complete.")
    yield
    logger.info("Application shutting down.")


# ── App factory ───────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Analyzes social-media content using local ML/NLP models "
        "(DistilBERT, TF-IDF, OpenCV, Tesseract) with Gemini for recommendations."
    ),
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
origins = [
    settings.frontend_url,
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]
if "*" not in origins and not settings.frontend_url:
    origins.append("*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.frontend_url == "*" else origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(router)


@app.api_route("/", methods=["GET", "HEAD"], include_in_schema=False)
async def root():
    return {
        "message": f"{settings.app_name} API",
        "version": settings.app_version,
        "docs": "/docs",
    }
