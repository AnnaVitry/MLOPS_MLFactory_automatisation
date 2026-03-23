# On utilise l'image officielle Prefect avec Python 3.12 (comme ton environnement)
FROM prefecthq/prefect:3-python3.12

# On installe uv pour une gestion ultra-rapide des dépendances
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
ENV UV_SYSTEM_PYTHON=1

WORKDIR /app

# On installe les dépendances
COPY pyproject.toml .
RUN uv pip install .

# On copie le reste du code
COPY . /app

# On s'assure que Python trouve les dossiers (src...)
ENV PYTHONPATH=/app