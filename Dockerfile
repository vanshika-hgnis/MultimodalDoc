# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps commonly needed for: EasyOCR / OpenCV / PDF rendering / Tesseract (optional)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    poppler-utils \
    tesseract-ocr \
    libgl1 \
    libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy all project files
COPY . /app

# Expose FastAPI
EXPOSE 8000

# Default command (API). Worker runs via docker-compose override.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
