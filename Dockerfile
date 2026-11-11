# Base image: small official Python image
FROM python:3.12-slim

# Avoid .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Working directory inside the container
WORKDIR /app

# Install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Run as a non-root user
RUN useradd --create-home appuser
USER appuser

# Document the port the app listens on
EXPOSE 5000

# Start the app with gunicorn (production-grade server)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]

