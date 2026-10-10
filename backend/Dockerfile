FROM python:3.11-slim-bookworm

WORKDIR /app

COPY pyproject.toml README.md alembic.ini ./
COPY app ./app

RUN pip install --no-cache-dir .

EXPOSE 8000

# Schema first, then serve. Needs DATABASE_URL.
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.composition:build_app --factory --host 0.0.0.0 --port 8000"]
