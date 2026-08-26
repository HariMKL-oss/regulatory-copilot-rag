FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Run benchmark verification at build time
RUN python src/evaluator.py

EXPOSE 8002
EXPOSE 8503

CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8002"]
