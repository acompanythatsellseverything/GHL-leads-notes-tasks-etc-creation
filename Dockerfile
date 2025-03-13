# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Flask app into the container
COPY . .

# Install curl
RUN apt-get update && apt-get install -y curl

# Expose the port Flask runs on
EXPOSE 5007

# Command to start the Flask server
CMD ["flask", "run", "--host=0.0.0.0", "--port=5007"]

HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:5007/health || exit 1
