# Use slim python 3.11 image to satisfy pyproject.toml requirement (^3.10)
FROM python:3.11-slim

WORKDIR /app

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps (build-essential + curl for poetry)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy requirements
COPY exa-scheduler/pyproject.toml .
# COPY exa-scheduler/poetry.lock . # Uncomment if you have a lock file

# Install dependencies
# --no-root: Skips installing the project itself (fixes the "No file/folder" error)
# --only main: Skips dev dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

# Copy source code
COPY exa-scheduler/src/ src/
COPY exa-scheduler/config/ config/

# Expose port
EXPOSE 8000

# Create user for security
# NOTE: Commented out to fix Fly.io volume permission issues. 
# Fly volumes are owned by root, so the app needs to run as root to write to /app/data.
# RUN useradd -m appuser && chown -R appuser /app
# USER appuser

# CMD
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
