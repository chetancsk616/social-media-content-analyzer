FROM python:3.11-slim

# Install system dependencies: Tesseract OCR, OpenGL & required image libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip and install CPU-only PyTorch for DistilBERT sentiment model
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.3.1 --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY . .

# Expose default port
EXPOSE 8000

# Set environment defaults
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Start command using uvicorn binding to 0.0.0.0 and dynamic PORT
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
