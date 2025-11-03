FROM python:3.12-slim

# Install system dependencies including Rust
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Install wallust
RUN cargo install wallust

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
