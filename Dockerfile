FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY scripts/download_model.py scripts/download_model.py

ENV EMBEDDING_MODEL=all-MiniLM-L6-v2
ENV EMBEDDING_CACHE_DIR=/root/.cache/huggingface

RUN python scripts/download_model.py


FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /usr/local /usr/local
COPY --from=builder /root/.cache /home/appuser/.cache

RUN useradd -m -u 1001 appuser && \
    mkdir -p /tmp/uploads /app/data/chroma /app/eval_results /app/model_cache && \
    chown -R appuser:appuser /tmp/uploads /app/data /app/eval_results /app/model_cache /home/appuser/.cache

COPY --chown=appuser:appuser . .

USER appuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/v1/health')"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]