# Dockerfile placé à la racine du projet
FROM python:3.13-slim

WORKDIR /app

COPY backend/ ./backend
COPY ai_module/ ./ai_module

RUN pip install --no-cache-dir -r ./backend/requirements.txt gunicorn

ENV PORT=8080
ENV PYTHONPATH=/app

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 backend.main:app