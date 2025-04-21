# Use official Python image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies (e.g., for PostgreSQL support)
RUN apt-get update \
    && apt-get install -y libpq-dev gcc \
    && pip install --upgrade pip

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Expose default Flask port
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]