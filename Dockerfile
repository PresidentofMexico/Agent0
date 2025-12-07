# Use slim python image (Debian based easier for some deps like chroma)
FROM python:3.9-slim

WORKDIR /app

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps (if needed for typical agents)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements/pyproject
COPY exa-scheduler/pyproject.toml .
# Install manually or use pip install . if setup
RUN pip install --no-cache-dir .

# Copy source
COPY exa-scheduler/src/ src/
COPY exa-scheduler/config/ config/

# Expose port
EXPOSE 8000

# Create user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# CMD
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
