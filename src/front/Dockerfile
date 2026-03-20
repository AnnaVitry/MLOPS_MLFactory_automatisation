FROM python:3.11-slim
WORKDIR /app

RUN pip install uv 
COPY pyproject.toml uv.lock ./

RUN uv sync

COPY src/front/ ./src/front/
EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "src/front/app.py", "--server.port=8501", "--server.address=0.0.0.0"]