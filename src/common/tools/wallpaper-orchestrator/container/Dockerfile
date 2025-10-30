# Wallpaper Processor Container
# Contains all dependencies for processing wallpapers with effects

FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    imagemagick \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy module files
COPY wallpaper_processor/ /app/wallpaper_processor/
COPY dotfiles_logging/ /app/dotfiles_logging/

# Install Python dependencies
RUN pip install --no-cache-dir \
    pydantic>=2.11.9 \
    pillow>=10.0.0 \
    dynaconf>=3.2.0 \
    rich>=13.0.0

# Copy entrypoint script
COPY entrypoint.py /app/entrypoint.py

# Set Python path
ENV PYTHONPATH=/app

# Create input/output directories
RUN mkdir -p /input /output

# Run entrypoint
ENTRYPOINT ["python", "/app/entrypoint.py"]

