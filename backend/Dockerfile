FROM python:3.12.7

WORKDIR /app

COPY requirements.txt .
COPY backend/ backend/

RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONPATH=/app

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]