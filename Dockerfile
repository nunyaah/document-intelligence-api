FROM python:3.11-slim AS builder

WORKDIR /app

# Install build deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Pre-download embedding model
COPY scripts/download_model.py scripts/download_model.py
ENV EMBEDDING_MODEL=all-MiniLM-L6-v2
ENV EMBEDDING_CACHE_DIR=/root/.cache/huggingface
RUN python scripts/download_model.py


FROM python:3.11-slim

WORKDIR /app

# Copy installed packages
COPY --from=builder /root/.local /root/.local
COPY --from=builder /root/.cache /root/.cache

# Create non-root user
RUN useradd -m -u 1001 appuser && \
    mkdir -p /tmp/uploads /app/data/chroma /app/eval_results /app/model_cache && \
    chown -R appuser:appuser /tmp/uploads /app/data /app/eval_results /app/model_cache

ENV PATH=/root/.local/bin:$PATH

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
