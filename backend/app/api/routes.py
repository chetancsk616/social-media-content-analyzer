"""
FastAPI route handlers.

Handlers are thin — all business logic lives in the orchestrator/services.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.analysis import AnalysisResponse, HealthResponse, TextAnalysisRequest
from app.services import sentiment_service
from app.services.analysis_orchestrator import (
    run_analysis_on_file,
    run_analysis_on_text,
)
from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

router = APIRouter(prefix="/api")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    tags=["System"],
)
async def health_check() -> HealthResponse:
    """Returns application health status and capability flags."""
    import os
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        sentiment_model_loaded=sentiment_service.is_model_loaded(),
        gemini_configured=bool(
            settings.gemini_api_key or os.environ.get("GEMINI_API_KEY", "")
        ),
    )


@router.post(
    "/analyze",
    response_model=AnalysisResponse,
    summary="Analyze a PDF or image file",
    tags=["Analysis"],
    status_code=status.HTTP_200_OK,
)
async def analyze_file(
    file: UploadFile = File(..., description="PDF, PNG, JPG, or JPEG file"),
) -> AnalysisResponse:
    """
    Upload a PDF or image file for social-media content analysis.

    The pipeline automatically chooses between PyMuPDF text extraction
    and Tesseract OCR based on the content of the file.
    """
    try:
        return await run_analysis_on_file(file)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except RuntimeError as exc:
        logger.error("Analysis runtime error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during file analysis: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis. Please try again.",
        ) from exc


@router.post(
    "/analyze/text",
    response_model=AnalysisResponse,
    summary="Analyze raw text",
    tags=["Analysis"],
    status_code=status.HTTP_200_OK,
)
async def analyze_text(request: TextAnalysisRequest) -> AnalysisResponse:
    """
    Analyze a raw social-media post provided as plain text.
    Useful for testing or when the content is already available as text.
    """
    try:
        return await run_analysis_on_text(request.text)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        logger.exception("Unexpected error during text analysis: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during analysis. Please try again.",
        ) from exc
