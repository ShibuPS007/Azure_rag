FROM python:3.12.7

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

CMD ["streamlit", "run", "frontend/app_1.py", "--server.port=8501", "--server.address=0.0.0.0"]