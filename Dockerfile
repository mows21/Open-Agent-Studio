# Dockerfile for Open Agent Studio (VPS/Headless deployment)
# Optimized for browser automation only

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Playwright dependencies
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    # OCR support
    tesseract-ocr \
    tesseract-ocr-eng \
    # Utilities
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements_conversational.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements_conversational.txt

# Install Playwright browsers (chromium only for smaller image)
RUN playwright install chromium
RUN playwright install-deps

# Copy application code
COPY . .

# Create config directory
RUN mkdir -p /app/workflows /app/logs

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Expose API port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Run API server
CMD ["python", "vps_api_server.py"]
