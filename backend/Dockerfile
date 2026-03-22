FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory for SQLite DB
RUN mkdir -p data

EXPOSE 8000

# run.py handles first-run setup (train model, seed DB) and starts uvicorn
CMD ["python", "run.py"]
