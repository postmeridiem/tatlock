FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    HOSTNAME=0.0.0.0 \
    PORT=8000 \
    OLLAMA_HOST=http://ollama:11434

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    sqlite3 \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements-lock.txt ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

RUN chmod +x docker-entrypoint.sh docker-init.py && \
    groupadd --system tatlock && \
    useradd --system --create-home --gid tatlock tatlock && \
    chown -R tatlock:tatlock /app

USER tatlock

EXPOSE 8000

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["python", "main.py"]
