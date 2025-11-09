FROM python:3.13-alpine

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask twilio flask-wtf

# Copy application
COPY phishing_demo.py .
COPY logo.png .

# Expose port
EXPOSE 9999

# Run the application
CMD ["python", "phishing_demo.py"]
