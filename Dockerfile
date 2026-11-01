FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY water_monitoring ./water_monitoring
COPY tests ./tests
RUN mkdir -p /app/data
EXPOSE 8000
CMD ["uvicorn", "water_monitoring.api:app", "--host", "0.0.0.0", "--port", "8000"]
