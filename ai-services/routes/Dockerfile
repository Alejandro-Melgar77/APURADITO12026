FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    ROUTE_MODEL_DIR=/app/models

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app ./app
RUN mkdir -p /app/models

EXPOSE 8013
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8013}
