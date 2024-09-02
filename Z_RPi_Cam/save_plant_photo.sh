#!/bin/bash

# Directory where images will be saved
DIR=~/growth

# Infinite loop
while true
do
    # Generate filename based on current date and time
    FILENAME="plant-$(date +%Y-%m-%d-%H-%M-%S).jpg"

    # Capture the image
    raspistill -o "$DIR/$FILENAME"

    # Wait for 60 seconds
    sleep 60
done