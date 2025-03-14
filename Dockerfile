# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Flask app into the container
COPY . .

# Install curl (needed for health monitoring)
RUN apt-get update && apt-get install -y curl docker.io

# Expose the port Flask runs on
EXPOSE 5007

# Make the health monitoring script executable
RUN chmod +x /app/docker_health_monitor.sh

# Define the health check for Docker
HEALTHCHECK --interval=5s --timeout=5s --retries=3 CMD curl -f http://localhost:5007/healthh || exit 1

# Start both Flask and the monitoring script
CMD ["/bin/sh", "-c", "/app/docker_health_monitor.sh & flask run --host=0.0.0.0 --port=5007"]
