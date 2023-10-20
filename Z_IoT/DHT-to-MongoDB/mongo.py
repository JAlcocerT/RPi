### Testing MongoDB Connection ###

#pip install pymongo


import pymongo

# MongoDB connection parameters
mongo_host = "192.168.1.100"  # Change to your MongoDB host if needed
mongo_port = 27017        # Change to the MongoDB port if needed
mongo_username = "yourusername"  # Replace with your MongoDB username
mongo_password = "yourpassword"  # Replace with your MongoDB password

try:
    # Create a MongoDB client
    client = pymongo.MongoClient(host=mongo_host, port=mongo_port, username=mongo_username, password=mongo_password)

    # Check if the connection is successful by listing the database names
    db_names = client.list_database_names()

    # Print a success message and list of database names
    print("Successfully connected to MongoDB!")
    print("Available databases:")
    for db_name in db_names:
        print(f"- {db_name}")

except Exception as e:
    # If there's an error, print an error message
    print(f"Error connecting to MongoDB: {e}")

finally:
    # Close the MongoDB client
    client.close()