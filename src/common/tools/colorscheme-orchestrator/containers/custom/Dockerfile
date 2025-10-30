FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create working directories
RUN mkdir -p /input /output /app

# Set working directory
WORKDIR /app

# Copy colorscheme-generator module (will be added during build)
COPY colorscheme-generator /app/colorscheme-generator

# Install colorscheme-generator with custom backend dependencies
RUN pip install --no-cache-dir /app/colorscheme-generator

# Copy entrypoint script
COPY entrypoint.py /app/entrypoint.py
RUN chmod +x /app/entrypoint.py

# Set entrypoint
ENTRYPOINT ["python", "/app/entrypoint.py"]

