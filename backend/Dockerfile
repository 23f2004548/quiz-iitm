# Use a slim Python 3.11 image
FROM python:3.11-slim

# Install system dependencies (build-essential helps compile binary wheels like bcrypt if needed)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the port (Railway injects PORT automatically)
EXPOSE 5000

# Start gunicorn, binding to the port provided by Railway (defaulting to 5000)
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} run:app
