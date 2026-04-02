# Étape 1 : Construction de l'environnement avec UV
FROM python:3.12-slim
WORKDIR /app

RUN pip install uv
COPY pyproject.toml . 
RUN uv sync --python 3.12
COPY src ./src

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
