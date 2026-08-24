# Social Media Content Analyzer

A production-quality full-stack application that analyzes social-media content from PDF and image uploads using a local ML/NLP pipeline, and generates actionable recommendations via the Google Gemini API.

---

## Description

Social Media Content Analyzer accepts uploaded PDF documents or image files containing social-media posts. It extracts text locally (PyMuPDF for PDFs, OpenCV + Tesseract OCR for images and scanned PDFs), runs a multi-stage NLP analysis using local models, and returns an **Engagement Optimization Score** alongside detailed sub-scores, keywords, hashtag suggestions, and AI-generated recommendations.

The application is intentionally designed so that **95% of the analysis pipeline runs locally** — no cloud APIs for NLP. Only recommendation generation and post rewriting are delegated to the Gemini API, and the app works in full without a Gemini key (showing local analysis only).

---

## Features

- **PDF text extraction** — PyMuPDF with automatic fallback to Tesseract OCR for scanned documents
- **Image OCR** — OpenCV preprocessing pipeline (grayscale → denoise → adaptive threshold → deskew) + Tesseract
- **Sentiment analysis** — DistilBERT transformer model, loaded locally at startup
- **Keyword extraction** — TF-IDF with scikit-learn, sentence-level IDF, fallback to frequency ranking
- **Readability metrics** — Flesch Reading Ease computed locally
- **Hook analysis** — Custom deterministic scoring algorithm with regex pattern matching
- **CTA detection** — Weighted pattern detection for call-to-action phrases
- **Content clarity scoring** — Heuristic analysis of sentence length, caps, punctuation, vocabulary complexity, repetition
- **Hashtag suggestions** — Generated from keywords, noun phrases, and existing hashtags (no social API)
- **Engagement Optimization Score** — Configurable weighted composite of all sub-scores
- **AI recommendations** — Gemini API for natural-language suggestions, improved post rewrite, and alternative hooks
- **Graceful Gemini fallback** — Full local analysis is always displayed regardless of Gemini availability
- **Drag-and-drop upload** — react-dropzone with file validation and progress indicator
- **Text paste mode** — Direct text input for testing
- **Results dashboard** — Recharts radial score, score cards, sentiment, metrics, keyword chips, hashtag chips with copy, recommendations, improved post with copy

---

## Architecture

```
User
 |
 | PDF / JPG / PNG / Text
 v
React Frontend (Vite + Tailwind CSS + Recharts)
 |
 v
FastAPI Backend (Python 3.11+)
 |
 +------------------------------+
 |                              |
 | PDF                          | Image
 v                              v
PyMuPDF                      OpenCV
 |                              |
 | (if scanned)            Grayscale → Denoise
 +---> Tesseract OCR <--+  → Threshold → Deskew
                        |        |
                        |   Tesseract OCR
                        |        |
                        +---------+
                              |
                              v
                      Extracted Text
                              |
                              v
                     Text Preprocessing
                     (normalization, tokenization)
                              |
                  +-----------+-----------+
                  |           |           |
                  v           v           v
            DistilBERT    TF-IDF     Readability
            Sentiment    Keywords   (Flesch R.E.)
                  |           |           |
                  +-----------+-----------+
                              |
                              v
                   Custom Scoring Engine
                  /         |         \
            Hook         CTA        Clarity
            Score        Score      Score
                  \         |         /
                   +---------+--------+
                              |
                              v
               Engagement Optimization Score /100
                              |
                              v
                         Gemini API
                   (recommendations only)
                              |
                              v
                      React Dashboard
```

---

## Tech Stack

### Local Processing

| Component | Library | Purpose |
|-----------|---------|---------|
| PDF extraction | PyMuPDF (`fitz`) | Page-by-page text extraction |
| Image preprocessing | OpenCV (`cv2`) | Grayscale, denoise, threshold, deskew |
| OCR | Tesseract + `pytesseract` | Text from images and scanned PDFs |
| Sentiment | Hugging Face Transformers + PyTorch | DistilBERT SST-2 fine-tuned |
| Keyword extraction | scikit-learn TF-IDF | Unigram + bigram keywords |
| Readability | Custom implementation | Flesch Reading Ease |
| Scoring | Custom algorithms | Hook, CTA, clarity, structure scores |
| API framework | FastAPI + Uvicorn | REST API with Pydantic validation |

### External AI

| Component | Service | Purpose |
|-----------|---------|---------|
| Recommendations | Google Gemini API | Natural-language suggestions, post rewriting |

> Gemini is used **only** for recommendation generation and post rewriting.  
> All other analysis (extraction, OCR, sentiment, readability, scoring, keywords) runs entirely locally.

---

## Installation

### Prerequisites

- Python 3.11+
- Node.js 18+
- Tesseract OCR (see instructions below)

### Tesseract Installation

**Windows:**
```
Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
Install to C:\Program Files\Tesseract-OCR\
Add C:\Program Files\Tesseract-OCR\ to your PATH
```

**macOS:**
```bash
brew install tesseract
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install tesseract-ocr
```

### Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp ../.env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Frontend Setup

```bash
cd frontend
npm install
```

---

## Environment Variables

Copy `.env.example` to `.env` in the `backend/` directory:

```bash
cp .env.example backend/.env
```

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key (optional) | — |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |
| `MAX_FILE_SIZE_MB` | Maximum upload size in MB | `10` |

> The application works without a `GEMINI_API_KEY`. Local analysis always runs. AI recommendations show "temporarily unavailable" if the key is missing.

---

## Running Locally

### Start the backend

```bash
cd backend
# Activate venv first (see above)
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

> **Note:** The DistilBERT model (~67 MB) is downloaded from Hugging Face Hub on first startup and cached locally. Subsequent starts are fast.

### Start the frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## API Endpoints

### `GET /api/health`

Returns application health and capability flags.

```json
{
  "status": "ok",
  "version": "1.0.0",
  "sentiment_model_loaded": true,
  "gemini_configured": true
}
```

### `POST /api/analyze`

Upload a PDF, PNG, JPG, or JPEG file for analysis.

**Request:** `multipart/form-data` with `file` field.

**Response:** `AnalysisResponse` (see schema below).

### `POST /api/analyze/text`

Analyze raw text directly.

**Request:**
```json
{
  "text": "Your social media post content here..."
}
```

**Response:** `AnalysisResponse`

### Response Schema

```json
{
  "filename": "post.pdf",
  "file_type": "pdf",
  "extraction_method": "pymupdf",
  "extracted_text": "...",
  "char_count": 342,
  "sentiment": { "label": "POSITIVE", "confidence": 0.94 },
  "metrics": {
    "word_count": 120,
    "sentence_count": 8,
    "avg_sentence_length": 15.0,
    "avg_word_length": 4.8,
    "readability_score": 76.1,
    "readability_label": "Easy",
    "paragraph_count": 3
  },
  "keywords": ["artificial intelligence", "engagement", "strategy"],
  "hashtags": ["#ArtificialIntelligence", "#ContentStrategy"],
  "hook_analysis": { "score": 78, "feedback": "..." },
  "cta_analysis": { "score": 64, "feedback": "...", "detected_phrases": ["comment below"] },
  "scores": {
    "hook": 78,
    "cta": 64,
    "clarity": 82,
    "readability": 76,
    "structure": 70,
    "sentiment_score": 78,
    "keyword_score": 85,
    "overall": 75
  },
  "ai_recommendations": {
    "available": true,
    "recommendations": ["..."],
    "strengths": ["..."],
    "weaknesses": ["..."],
    "improved_post": "...",
    "alternative_hooks": ["..."]
  }
}
```

---

## ML Approach

### Sentiment Analysis (DistilBERT)

Uses `distilbert-base-uncased-finetuned-sst-2-english` from Hugging Face. The model is loaded into memory once at application startup via FastAPI's lifespan handler and reused for every request. Input is truncated to 512 tokens. Returns `POSITIVE` or `NEGATIVE` with confidence.

### Keyword Extraction (TF-IDF)

Uses `sklearn.feature_extraction.text.TfidfVectorizer` with `ngram_range=(1, 2)` and English stop words. Because we have a single document, each sentence is treated as a pseudo-document to give IDF meaningful variance. Scores are summed across sentences. Falls back to frequency-based extraction for texts under 20 words.

### Readability (Flesch Reading Ease)

Implemented locally: `206.835 - 1.015 × (words/sentences) - 84.6 × (syllables/words)`. Syllables are counted with a custom rule-based algorithm (vowel clusters minus silent-e). Scores ≥ 80 = Easy, 60–79 = Moderate, < 60 = Difficult.

### Hook Scoring

Deterministic regex-based algorithm evaluating the first 1–2 sentences. Signals considered: question marks, question words (what/how/why), direct audience address (you/your), numbers/statistics, power/emotional words (shocking/secret/revealed), imagination openers (imagine/what if), benefit words (save/earn/boost), urgency phrases, and opening length. Generic filler phrases (hello everyone, happy to share) apply penalties.

### CTA Scoring

Weighted pattern detection across the full post. Patterns are grouped by strength: direct purchase/signup actions (high weight) → engagement actions (comment/share/tag) → traffic actions (click/visit) → passive actions (like/follow) → urgency modifiers (low weight). Score is the sum of matched pattern weights, clamped to 100.

### Engagement Optimization Score

Configurable weighted average: Hook (25%) + CTA (20%) + Readability (15%) + Clarity (15%) + Sentiment (10%) + Keywords (10%) + Structure (5%). Weights are defined in `backend/app/core/config.py` and can be changed without modifying scoring logic.

---

## Running Tests

```bash
cd backend
# Activate virtual environment first
pytest tests/ -v
```

Tests mock the Gemini API — no real API key required.

---

## Limitations

- The **Engagement Optimization Score** is a heuristic analytical score. It is NOT a scientifically validated predictor of actual social-media engagement. Platform algorithms, audience size, timing, and other factors not considered here will affect real-world performance.
- OCR accuracy depends on image quality. Very low-resolution or heavily distorted images may yield poor results.
- The DistilBERT sentiment model is trained on English SST-2 data. Accuracy on non-English or heavily emoji-based content may be lower.
- Gemini recommendations require a valid API key and network access to Google's servers.

---

## Deployment

### Backend (example: Railway / Render)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Set environment variables on your hosting platform. Ensure Tesseract is installed on the deployment image (e.g., add `apt-get install -y tesseract-ocr` to your Dockerfile).

### Frontend (example: Vercel / Netlify)

```bash
cd frontend
npm run build
# Deploy the dist/ directory
```

Update `vite.config.js` proxy or set `VITE_API_BASE_URL` to point to your deployed backend URL.

### Docker (optional)

A `Dockerfile` for the backend should install Tesseract, Python dependencies, and run Uvicorn. The frontend can be served as a static build via Nginx or a CDN.

---

## Project Structure

```
social-media-content-analyzer/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DropZone.jsx
│   │   │   ├── ExtractedText.jsx
│   │   │   ├── HashtagSection.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── ImprovedPost.jsx
│   │   │   ├── KeywordSection.jsx
│   │   │   ├── MetricsCard.jsx
│   │   │   ├── OverallScore.jsx
│   │   │   ├── ProcessingState.jsx
│   │   │   ├── Recommendations.jsx
│   │   │   ├── ScoreCards.jsx
│   │   │   └── SentimentCard.jsx
│   │   ├── hooks/
│   │   │   └── useAnalysis.js
│   │   ├── pages/
│   │   │   ├── ResultsPage.jsx
│   │   │   └── UploadPage.jsx
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   └── vite.config.js
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── schemas/
│   │   │   └── analysis.py
│   │   ├── services/
│   │   │   ├── analysis_orchestrator.py
│   │   │   ├── gemini_service.py
│   │   │   ├── hashtag_service.py
│   │   │   ├── keyword_service.py
│   │   │   ├── ocr_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── preprocessing_service.py
│   │   │   ├── readability_service.py
│   │   │   ├── scoring_service.py
│   │   │   └── sentiment_service.py
│   │   └── main.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── test_analysis.py
│   │   ├── test_health.py
│   │   ├── test_keywords.py
│   │   ├── test_readability.py
│   │   └── test_scoring.py
│   └── requirements.txt
│
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```
