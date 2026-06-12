# Build from the repo root so the shared ml/ package can be included:
#   docker build -f services/api/Dockerfile .
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY services/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/api/ .
COPY ml/ ./ml/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
