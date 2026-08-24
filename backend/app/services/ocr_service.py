"""
OCR service using OpenCV for image preprocessing and Tesseract for text extraction.

Pipeline per image:
  Raw image → Grayscale → Denoise → Adaptive threshold → Optional deskew → Tesseract

For scanned PDFs, each page is rendered to an image via PyMuPDF, then processed
through the same pipeline.
"""

from __future__ import annotations

import logging
import math
from typing import Optional

import cv2
import numpy as np
from PIL import Image
import pytesseract

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


# ── Image preprocessing ───────────────────────────────────────────────────────

def _to_grayscale(image: np.ndarray) -> np.ndarray:
    """Convert BGR or BGRA image to grayscale."""
    if len(image.shape) == 3:
        if image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2GRAY)
        else:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


def _denoise(image: np.ndarray) -> np.ndarray:
    """Apply non-local means denoising appropriate for document images."""
    return cv2.fastNlMeansDenoising(image, h=10)


def _threshold(image: np.ndarray) -> np.ndarray:
    """Apply adaptive thresholding to binarise the image."""
    return cv2.adaptiveThreshold(
        image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,  # block size
        2,   # constant subtracted from mean
    )


def _deskew(image: np.ndarray) -> np.ndarray:
    """
    Detect and correct skew in a document image.
    Uses the Hough line transform approach. Falls back to the original
    image if deskew detection fails.
    """
    try:
        # Find coordinates of non-white pixels
        coords = np.column_stack(np.where(image < 128))
        if len(coords) < 10:
            return image

        angle = cv2.minAreaRect(coords)[-1]

        # minAreaRect angle is in (-90, 0]; convert to a usable rotation angle
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle

        # Only deskew if the tilt is significant
        if abs(angle) < 0.5:
            return image

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
        return rotated
    except Exception as exc:
        logger.debug("Deskew failed (non-critical): %s", exc)
        return image


def preprocess_image_for_ocr(image: np.ndarray) -> np.ndarray:
    """Run the full preprocessing pipeline on an OpenCV image array."""
    gray = _to_grayscale(image)
    denoised = _denoise(gray)
    thresholded = _threshold(denoised)
    deskewed = _deskew(thresholded)
    return deskewed


# ── OCR on image files (JPG / PNG) ────────────────────────────────────────────

def ocr_image_file(file_path: str) -> str:
    """
    Run OCR on a JPG / PNG / JPEG file.

    Returns:
        Extracted text string.

    Raises:
        ValueError: if the image cannot be decoded.
        RuntimeError: if Tesseract is not installed or OCR fails.
    """
    # Load with OpenCV
    image = cv2.imread(file_path)
    if image is None:
        # Try via Pillow as a fallback loader
        try:
            pil_img = Image.open(file_path).convert("RGB")
            image = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
        except Exception as exc:
            raise ValueError(f"Cannot decode image file: {exc}") from exc

    processed = preprocess_image_for_ocr(image)

    # Convert processed (grayscale uint8) to PIL Image for pytesseract
    pil_processed = Image.fromarray(processed)

    try:
        text = pytesseract.image_to_string(
            pil_processed,
            config=settings.tesseract_config,
        )
    except pytesseract.TesseractNotFoundError as exc:
        raise RuntimeError(
            "Tesseract OCR is not installed or not found in PATH. "
            "Please install Tesseract: https://github.com/tesseract-ocr/tesseract"
        ) from exc
    except Exception as exc:
        raise RuntimeError(f"OCR processing failed: {exc}") from exc

    if not text.strip():
        raise RuntimeError(
            "No readable text detected in the image. "
            "The image may be too blurry, low-contrast, or contain no text."
        )

    logger.info("OCR extracted %d chars from image %s", len(text), file_path)
    return text


# ── OCR on scanned PDF pages ──────────────────────────────────────────────────

def ocr_pdf_pages(file_path: str) -> str:
    """
    Render each PDF page to an image and run OCR.
    Uses PyMuPDF for rendering (imported here to avoid circular imports).

    Returns:
        Combined OCR text from all pages.
    """
    import fitz  # PyMuPDF — local import to keep dependency explicit

    try:
        doc = fitz.open(file_path)
    except Exception as exc:
        raise ValueError(f"Cannot open PDF for OCR: {exc}") from exc

    page_texts: list[str] = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        # Render at 2x zoom for better OCR accuracy
        mat = fitz.Matrix(2.0, 2.0)
        pix = page.get_pixmap(matrix=mat, colorspace=fitz.csGRAY)
        # Convert pixmap to numpy array
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(
            pix.height, pix.width
        )

        # Apply thresholding and deskew (grayscale already)
        denoised = _denoise(img_array)
        thresholded = _threshold(denoised)
        deskewed = _deskew(thresholded)

        pil_img = Image.fromarray(deskewed)
        try:
            page_text = pytesseract.image_to_string(
                pil_img,
                config=settings.tesseract_config,
            )
            page_texts.append(page_text)
        except pytesseract.TesseractNotFoundError as exc:
            raise RuntimeError(
                "Tesseract OCR is not installed. "
                "Install it from https://github.com/tesseract-ocr/tesseract"
            ) from exc
        except Exception as exc:
            logger.warning("OCR failed on page %d: %s", page_num, exc)
            page_texts.append("")

    doc.close()
    combined = "\n\n".join(t for t in page_texts if t.strip())
    logger.info(
        "OCR on PDF %s: %d pages, %d chars extracted.",
        file_path,
        len(page_texts),
        len(combined),
    )
    return combined
