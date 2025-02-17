# Use a lightweight Python image
FROM python:3.12-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire Flask app into the container
COPY . .

# Expose the port Flask runs on
EXPOSE 5000

# Command to start the Flask server
CMD ["flask", "run", "--host=0.0.0.0"]
