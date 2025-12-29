FROM python:3.13-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml .
# COPY uv.lock .

# Install dependencies (generates uv.lock during build)
RUN uv sync --no-dev

# Copy source code
COPY src/ src/
COPY main.py .

# Create data directory for SQLite
RUN mkdir -p data

# Expose the default FastMCP port
EXPOSE 8000

# Run server
CMD ["uv", "run", "python", "main.py"]
