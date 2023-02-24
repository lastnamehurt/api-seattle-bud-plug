# Use the official Python image as the base image
FROM --platform=linux/amd64 python:3.9-slim

# Set the working directory to /app
WORKDIR /src

# Copy the requirements file into the container and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container
COPY . .

# Set the PORT environment variable to the port that Heroku assigns to the app
ENV PORT=8000

# Expose the port that the app will run on
EXPOSE $PORT

# Start the app using a shell script
CMD uvicorn src.api:app --host 0.0.0.0 --port $PORT
