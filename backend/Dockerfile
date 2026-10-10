FROM python:3.11-slim-bookworm

WORKDIR /app

COPY pyproject.toml README.md ./
COPY app ./app

RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["uvicorn", "app.composition:build_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
