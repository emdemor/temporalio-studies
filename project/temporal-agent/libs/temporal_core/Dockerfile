FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir .

COPY worker/ ./worker/
COPY workflows/ ./workflows/
COPY activities/ ./activities/

CMD ["python", "-m", "worker.main"]
