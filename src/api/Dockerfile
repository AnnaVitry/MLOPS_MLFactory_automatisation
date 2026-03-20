# Étape 1 : Construction de l'environnement avec UV
FROM python:3.11-slim
WORKDIR /app

RUN pip install uv
COPY pyproject.toml . 
RUN uv sync
COPY src/api/ ./src/api/

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]