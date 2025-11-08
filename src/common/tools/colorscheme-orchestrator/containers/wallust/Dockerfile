# Build stage for wallust
FROM rust:1.83-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install nightly toolchain for edition2024 support
RUN rustup toolchain install nightly && \
    rustup default nightly

# Install wallust
RUN cargo install wallust

# Final stage
FROM python:3.12-slim

# Copy wallust binary from builder
COPY --from=builder /usr/local/cargo/bin/wallust /usr/local/bin/wallust

# Create working directories
RUN mkdir -p /input /output /app

# Set working directory
WORKDIR /app

# Copy colorscheme-generator module (will be added during build)
COPY colorscheme-generator /app/colorscheme-generator

# Install colorscheme-generator
RUN pip install --no-cache-dir /app/colorscheme-generator

# Copy entrypoint script
COPY entrypoint.py /app/entrypoint.py
RUN chmod +x /app/entrypoint.py

# Set entrypoint
ENTRYPOINT ["python", "/app/entrypoint.py"]
