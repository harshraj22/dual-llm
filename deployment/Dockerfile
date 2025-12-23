FROM python:3.10-slim

WORKDIR /app

# Ensure logs are flushed immediately
ENV PYTHONUNBUFFERED=1

# Copy Requirements
COPY requirements.txt .

# Install Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Source Code
COPY src/ ./src/
COPY config.yaml .
COPY main.py .

# Entrypoint
CMD ["python", "main.py"]
