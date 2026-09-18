FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --default-timeout=120 --retries 10 -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "-k", "uvicorn_worker.UvicornWorker", "--workers", "2", "--bind", "0.0.0.0:8000"]