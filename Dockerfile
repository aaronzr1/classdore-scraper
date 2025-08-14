FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR .

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .

# Ensure our script is executable
RUN chmod +x railway.sh

# Command to run when container starts
CMD ["bash", "railway.sh"]