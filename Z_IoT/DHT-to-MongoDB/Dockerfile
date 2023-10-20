# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install system-level dependencies and MongoDB
RUN apt-get update && \
    apt-get install -y python3-dev python3-pip && \
    python3 -m pip install --upgrade pip setuptools wheel

# Copy the local code to the container
COPY Python2MongoDB.py /app/

# Install additional dependencies
RUN pip install Adafruit_DHT==1.4.0 pip install pymongo==4.5.0

# Run the Python script
CMD ["python", "Python2MongoDB.py"]m