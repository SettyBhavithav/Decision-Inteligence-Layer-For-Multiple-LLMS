# Multi-stage Docker build for Trust-Aware Multi-Agent Framework
FROM python:3.10-slim

# Set system-wide environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create work directory
WORKDIR /app

# Install system dependencies (build-essential for scikit-learn/numpy compilation if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all framework codebase elements
COPY . .

# Expose backend API and frontend Streamlit default ports
EXPOSE 8000
EXPOSE 8501

# Default action is overridden by docker-compose commands
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
