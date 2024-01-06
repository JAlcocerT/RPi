# Use an official Python runtime as the base image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Install system-level dependencies and MongoDB
RUN apt-get update && \
    apt-get install -y python3-dev python3-pip && \
    python3 -m pip install --upgrade pip setuptools wheel

RUN apt-get install -y git libgpiod2

# Copy the local code to the container
COPY Python2MongoDB.py /app/

# Install additional dependencies
#### to work with RPI 32bits / for 64 use the latest ~4.5.0
RUN pip install pymongo==3.6.0 

RUN pip3 install adafruit-circuitpython-dht==4.0.4
RUN pip3 install board==1.0


#RUN pip3 install --install-option="--force-pi" Adafruit_DHT
#RUN pip install Adafruit_DHT==1.4.0 #not working

# Building it from source
#RUN git clone https://github.com/adafruit/Adafruit_Python_DHT.git

# Navigate into the cloned directory and install
#WORKDIR Adafruit_Python_DHT
#RUN python3 setup.py install --force-pi


WORKDIR /app

# Run the Python script
CMD ["python", "Python2MongoDB.py"]