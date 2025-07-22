# Use the exact Python version for consistency and reproducibility
FROM python:3.11.9-slim

# Set up working directory (matches your FastAPI app folder structure)
WORKDIR /app

# Install necessary system packages (for PDF parsing/processing)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies separately to leverage Docker cache
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of your application code (including backend and frontend)
COPY . /app

# Expose FastAPI server port
EXPOSE 8000

# Start the FastAPI app, specifying correct module and instance (main:web_app)
CMD ["uvicorn", "backend.app.main:web_app", "--host", "0.0.0.0", "--port", "8000", "--lifespan", "off"]
