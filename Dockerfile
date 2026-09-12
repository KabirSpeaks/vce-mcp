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

# Install the package and its dependencies
RUN uv pip install --system -e .

# Expose port (default to 8000, but can be overridden)
EXPOSE 8000

# Create a non-root user and change ownership
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Allow all hosts for Streamable HTTP since Hugging Face acts as a reverse proxy
ENV VCE_MCP_ALLOWED_HOSTS="*"

# Run the HTTP server, picking up PORT from the environment
CMD ["vce-mcp", "serve-http", "--host", "0.0.0.0"]
