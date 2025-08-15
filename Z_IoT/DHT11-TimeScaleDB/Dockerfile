# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install system-level dependencies
RUN apt-get update && \
    apt-get install -y python3-dev python3-pip libpq-dev gcc && \
    python3 -m pip install --upgrade pip setuptools wheel

# Copy the local code to the container
COPY your_modified_python_script.py /app/

# Install additional dependencies
RUN pip install Adafruit_DHT psycopg2-binary

# Run the Python script
CMD ["python", "dht11_python_timescale.py"]
