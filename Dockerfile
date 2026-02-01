# Use a lightweight Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files or buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Run Gunicorn using the config file we created
CMD ["gunicorn", "-c", "gunicorn_config.py", "wsgi:app"]