# Use slim python 3.11 image to satisfy pyproject.toml requirement (^3.10)
FROM python:3.11-slim

WORKDIR /app

# Prevent python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps (build-essential is often needed for python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements/pyproject
COPY exa-scheduler/pyproject.toml .

# Install dependencies
# We verify the pyproject.toml matches the python version here
RUN pip install --no-cache-dir .

# Copy source code
COPY exa-scheduler/src/ src/
COPY exa-scheduler/config/ config/

# Expose port
EXPOSE 8000

# Create user for security
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# CMD
CMD ["uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", "8000"]
