"""
PDF text extraction service using PyMuPDF.

Strategy:
1. Open the PDF with PyMuPDF (fitz).
2. Extract text from each page.
3. If a page yields fewer characters than the configured threshold,
   treat the entire document as a scanned PDF and fall back to OCR.
4. Returns (text, extraction_method) so the caller always knows what was used.
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Tuple

import fitz  # PyMuPDF

from app.core.config import get_settings
from app.services.ocr_service import ocr_pdf_pages

logger = logging.getLogger(__name__)
settings = get_settings()


def extract_text_from_pdf(file_path: str | Path) -> Tuple[str, str]:
    """
    Extract text from a PDF file.

    Returns:
        (extracted_text, extraction_method)
        extraction_method is 'pymupdf' or 'tesseract_ocr'

    Raises:
        ValueError: if the file cannot be opened as a PDF.
        RuntimeError: if no text can be extracted at all.
    """
    file_path = Path(file_path)

    try:
        doc = fitz.open(str(file_path))
    except Exception as exc:
        logger.error("Failed to open PDF %s: %s", file_path, exc)
        raise ValueError(f"Cannot open PDF: {exc}") from exc

    pages_text: list[str] = []
    low_text_pages: list[int] = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")  # plain text extraction
        pages_text.append(text)
        if len(text.strip()) < settings.ocr_text_threshold:
            low_text_pages.append(page_num)

    doc.close()

    # Determine if the PDF is mostly text-based or scanned
    total_pages = len(pages_text)
    low_ratio = len(low_text_pages) / max(total_pages, 1)

    if low_ratio > 0.5:
        # More than half the pages have very little text — treat as scanned
        logger.info(
            "PDF %s appears scanned (%d/%d pages low-text). Using OCR.",
            file_path.name,
            len(low_text_pages),
            total_pages,
        )
        ocr_text = ocr_pdf_pages(str(file_path))
        if not ocr_text.strip():
            raise RuntimeError(
                "No text could be extracted from this PDF even with OCR. "
                "The document may be blank, encrypted, or corrupted."
            )
        return ocr_text, "tesseract_ocr"

    # Combine pages with paragraph separation
    combined = "\n\n".join(p for p in pages_text if p.strip())

    if not combined.strip():
        raise RuntimeError(
            "No extractable text found in this PDF. "
            "If the PDF is scanned, ensure Tesseract is installed."
        )

    logger.info(
        "PDF %s extracted with PyMuPDF (%d pages).",
        file_path.name,
        total_pages,
    )
    return combined, "pymupdf"
