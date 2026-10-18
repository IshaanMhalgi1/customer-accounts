
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY service/ ./service/
COPY sitecustomize.py .

EXPOSE 5000

CMD ["python", "-m", "flask", "--app", "service.routes", "run", "--host=0.0.0.0", "--port=5000"]
