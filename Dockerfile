FROM python:3.13-alpine

WORKDIR /app

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY phishing_demo.py .
COPY logo.png .
COPY templates/ templates/
COPY static/ static/

# Expose port
EXPOSE 9999

# Run with Gunicorn for production stability
# --bind 0.0.0.0:9999 - Listen on all interfaces
# --workers 1 - Single worker to maintain in-memory state consistency
# --threads 4 - Multiple threads per worker for concurrency
# --worker-class gthread - Use threaded worker
# --timeout 120 - Request timeout
# --keep-alive 5 - Keep-alive timeout
CMD ["gunicorn", "--bind", "0.0.0.0:9999", "--workers", "1", "--threads", "4", "--worker-class", "gthread", "--timeout", "120", "--keep-alive", "5", "--access-logfile", "-", "--error-logfile", "-", "phishing_demo:app"]
