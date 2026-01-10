FROM python:3.12-slim

WORKDIR /app

COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server /app/server
COPY config.py /app/config.py

ENV PYTHONPATH=/app

EXPOSE 8000
CMD ["python", "server/main.py"]
