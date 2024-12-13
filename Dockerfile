# Use the official Python image from the Docker Hub 
FROM python:3.11 AS base

# Set the working directory to /app
WORKDIR /app

# Copy requirements.txt into the application directory
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app

# Run the minio server

FROM minio/minio

CMD ["server", "/data"]

# Minio listens on port 9000.
EXPOSE 9000

# Run the upload microservice
FROM base AS upload_service

CMD ["python", "upload.py"]

# Flask listens on port 5000.
EXPOSE 5000