FROM python:3.11-slim

WORKDIR /app/BackEnd

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . /app

# Run app
CMD ["uvicorn", "BackEnd.main:app", "--host", "0.0.0.0", "--port", "8000"]
