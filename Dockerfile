# Use official Python runtime as a parent image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV UV_SYSTEM_PYTHON=1

# Install uv for fast package management
RUN pip install uv

# Copy project files
COPY pyproject.toml README.md ./
COPY src/ ./src/
COPY data/ ./data/

# Install the package and its dependencies
RUN uv pip install --system -e .

# Create a non-root user and change ownership
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Allow all hosts for Streamable HTTP since Render acts as a reverse proxy
ENV VCE_MCP_ALLOWED_HOSTS="*"

# Run the HTTP server, ensuring it binds to Render's dynamic $PORT (default 10000)
CMD ["sh", "-c", "vce-mcp serve-http --host 0.0.0.0 --port ${PORT:-10000}"]
