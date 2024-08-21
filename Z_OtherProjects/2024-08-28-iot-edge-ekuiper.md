---
title: Edge Analytics with Raspberry Pi
author: JAlcocerT
date: 2024-08-28 00:34:00 +0800
categories: [Make your Raspberry Useful]
tags: [IoT, Sensors]
---

Stream Processing at the IoT Edge

> Ekuiper works great when combined with [EMQx Broker](https://jalcocert.github.io/RPi/posts/rpi-mqtt/#install-mqtt-broker)

## Setup Ekuiper

Lets use the [Ekuiper Docker Image](https://hub.docker.com/r/lfedge/ekuiper)

```sh
docker run -p 9081:9081 -d --name ekuiper -e MQTT_SOURCE__DEFAULT__SERVER=tcp://broker.emqx.io:1883 lfedge/ekuiper:latest
```

`http://localhost:9081/`

## Using Ekuiper

https://ekuiper.org/docs/en/latest/getting_started/quick_start_docker.html


---

## FAQ

https://github.com/lf-edge/ekuiper

### AI/ML

* TF Lite - https://ekuiper.org/docs/en/latest/guide/ai/python_tensorflow_lite_tutorial.html
    * https://www.tensorflow.org/lite/guide


## Cassandra

Yes, you can push data from Python to Apache Cassandra, **a distributed NoSQL database**. To interact with Cassandra from Python, you'll need to use a Python driver for Cassandra. One popular driver for Cassandra is `cassandra-driver`.

Here's how you can use `cassandra-driver` to push data to a Cassandra database:

1. Install the `cassandra-driver` using pip:

   ```bash
   pip install cassandra-driver
   ```

2. Import the necessary modules and create a connection to your Cassandra cluster:

   ```python
   from cassandra.cluster import Cluster

   # Connect to your Cassandra cluster (replace with your cluster's contact points)
   cluster = Cluster(['127.0.0.1'])  # Use the IP addresses or hostnames of your Cassandra nodes
   session = cluster.connect()
   ```

3. Create a keyspace (database) and switch to it:

   ```python
   keyspace_name = 'your_keyspace_name'

   # Create a keyspace (if it doesn't exist)
   session.execute(f"CREATE KEYSPACE IF NOT EXISTS {keyspace_name} WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': 1}}")

   # Switch to the keyspace
   session.set_keyspace(keyspace_name)
   ```

4. Define your Cassandra table schema (CQL) and create the table:

   ```python
   table_name = 'your_table_name'

   # Define your table schema (CQL)
   create_table_query = f"""
   CREATE TABLE IF NOT EXISTS {table_name} (
       id UUID PRIMARY KEY,
       column1 text,
       column2 int
   )
   """

   # Create the table
   session.execute(create_table_query)
   ```

5. Insert data into the Cassandra table:

   ```python
   from cassandra.query import SimpleStatement

   # Define the insert query
   insert_query = f"INSERT INTO {table_name} (id, column1, column2) VALUES (?, ?, ?)"

   # Prepare the insert statement
   insert_statement = SimpleStatement(insert_query, consistency_level=1)

   # Insert data into the table
   session.execute(insert_statement, (uuid.uuid4(), 'value1', 42))
   ```

6. Close the Cassandra session and cluster when you're done:

   ```python
   session.shutdown()
   cluster.shutdown()
   ```

Make sure to replace `'your_keyspace_name'` and `'your_table_name'` with your desired keyspace and table names, and customize the table schema and data as needed.

With these steps, you can push data from Python to Cassandra using the `cassandra-driver` library. Be sure to have a running Cassandra cluster with the appropriate configuration and keyspace set up before running the code.


## KAFKA

Yes, Python can push data to Apache Kafka. Kafka is a distributed streaming platform that allows you to publish and consume streams of records, and there are Python libraries and clients available to work with Kafka.

One popular Python library for interacting with Kafka is `confluent-kafka-python`, which is a Python wrapper for the Confluent Kafka client. You can use this library to produce (push) data to Kafka topics.

Here's an example of how to use `confluent-kafka-python` to produce data to a Kafka topic:

First, you need to install the library using pip:

```bash
pip install confluent-kafka
```

Now, you can use the following Python code to produce data to a Kafka topic:

```python
from confluent_kafka import Producer

# Kafka broker address and topic name
bootstrap_servers = 'localhost:9092'  # Change this to your Kafka broker's address
topic = 'your_topic_name'              # Change this to your Kafka topic name

# Create a Kafka producer configuration
producer_config = {
    'bootstrap.servers': bootstrap_servers,
    # Other producer configuration options can be added here
}

# Create a Kafka producer instance
producer = Producer(producer_config)

try:
    # Produce a message to the Kafka topic
    message_key = 'key'           # Change this to your desired message key
    message_value = 'Hello, Kafka!'  # Change this to your message content

    producer.produce(topic, key=message_key, value=message_value)
    producer.flush()  # Flush the producer buffer to send the message

    print(f"Produced message: key={message_key}, value={message_value} to topic: {topic}")

except Exception as e:
    print(f"Error producing message: {str(e)}")

finally:
    producer.close()
```

In this code:

1. You import the `Producer` class from `confluent_kafka`.

2. You define the Kafka broker address (`bootstrap_servers`) and the Kafka topic name you want to produce data to.

3. You create a Kafka producer configuration dictionary, specifying the bootstrap servers.

4. You create a Kafka producer instance using the provided configuration.

5. Inside a try-except block, you produce a message to the Kafka topic, specifying a message key and message value. You can customize the key and value as needed.

6. You flush the producer buffer to ensure that the message is sent to Kafka.

7. Finally, you close the producer.

Make sure to replace `'localhost:9092'` with the address of your Kafka broker and `'your_topic_name'` with the name of the Kafka topic you want to use.

With this code, you can push data to Kafka from your Python application.

## REDIS



Redis is an open-source, in-memory data structure store used as a database, cache, message broker, and streaming engine. It is known for its high performance, scalability, and flexibility. Redis provides data structures such as strings, hashes, lists, sets, sorted sets with range queries, bitmaps, hyperloglogs, geospatial indexes, and streams.

Redis is open source software released under the BSD license. It is available for Linux, macOS, Windows, and FreeBSD.

Here are some of the key features of Redis:

In-memory data store: Redis stores data in memory, which makes it very fast.
Data structures: Redis supports a wide variety of data structures, including strings, hashes, lists, sets, sorted sets, bitmaps, hyperloglogs, geospatial indexes, and streams.
Scalability: Redis is highly scalable and can be used to support a large number of concurrent connections.
Flexibility: Redis is a very flexible tool that can be used for a variety of purposes, including caching, data streaming, and real-time applications.
Redis is a popular choice for a variety of applications, including:

Caching: Redis can be used to cache frequently accessed data, such as user profiles or product information. This can improve the performance of applications by reducing the number of times the database needs to be accessed.
Data streaming: Redis can be used to stream data in real time. This can be used for applications such as real-time analytics or live chat.
Real-time applications: Redis can be used to build real-time applications that require high performance and scalability. This includes applications such as social media platforms, gaming applications, and financial trading applications.


```py

import redis

# Create a connection to the Redis database
r = redis.Redis()

# Push the data to Redis
r.set("key", "value")

# Push a list of data to Redis
r.lpush("list", "item1", "item2")
```

You can push data from Python to Redis, an in-memory data store, using the `redis-py` library. `redis-py` is a popular Python client for Redis that allows you to interact with Redis from your Python applications.

Here's how you can use `redis-py` to push data to Redis:

1. Install the `redis-py` library using pip:

   ```bash
   pip install redis
   ```

2. Import the `redis` module and create a connection to your Redis server:

   ```python
   import redis

   # Connect to your Redis server
   redis_host = 'localhost'  # Replace with your Redis server's host or IP address
   redis_port = 6379         # Default Redis port
   redis_db = 0              # Default Redis database
   r = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
   ```

   Replace `'localhost'` with the address of your Redis server if it's running on a different host.

3. Push data (key-value pairs) to Redis:

   ```python
   # Define your key-value data
   key = 'your_key'
   value = 'your_value'

   # Push data to Redis
   r.set(key, value)
   ```

   You can also specify additional parameters like expiration time, if needed.

4. Retrieve data from Redis:

   ```python
   # Retrieve data from Redis
   retrieved_value = r.get(key)

   if retrieved_value is not None:
       print(f"Value for key '{key}': {retrieved_value.decode('utf-8')}")
   else:
       print(f"Key '{key}' not found in Redis.")
   ```

5. Close the Redis connection when you're done:

   ```python
   r.close()
   ```

These are the basic steps to push data from Python to Redis using `redis-py`. You can use various Redis data structures and commands depending on your use case, such as lists, sets, hashes, and more.

Make sure that you have a running Redis server with the appropriate configuration and access permissions before running the code.

### In memory data store

An in-memory data store, often referred to as an "in-memory database" or "in-memory data store," is a type of database system that primarily stores and manages data in the system's main memory (RAM) rather than on traditional disk storage devices. This means that data is held and processed in memory, which offers several advantages:

1. **Speed**: Data access and retrieval are extremely fast since there's no need to read from or write to slow disk drives. In-memory data stores can achieve low-latency and high-throughput operations, making them ideal for applications requiring rapid data access.

2. **Low Latency**: Because data is stored in RAM, there is minimal seek time or latency associated with accessing the data. This is particularly important for real-time or high-performance applications.

3. **Predictable Performance**: In-memory data stores provide consistent and predictable performance characteristics, making them suitable for applications where response times must be tightly controlled.

4. **Caching**: In-memory data stores are commonly used for caching frequently accessed data. This reduces the load on traditional databases and accelerates data retrieval for read-heavy workloads.

5. **No Disk I/O Overhead**: Since data isn't written to disk, there is no disk I/O overhead, which can be a significant bottleneck in traditional database systems.

6. **Data Integrity**: In-memory databases typically have mechanisms to ensure data consistency and durability, such as periodic snapshots to disk or replication to other nodes.

7. **Real-Time Analytics**: In-memory databases are often used for real-time analytics and data processing, where quick insights are required from large volumes of data.

However, there are also some limitations to in-memory data stores:

1. **Limited Storage**: In-memory data stores are constrained by the amount of available RAM, which may limit the volume of data that can be stored. This makes them less suitable for very large datasets.

2. **Data Durability**: In-memory data is volatile and can be lost if the system crashes or is restarted. Some in-memory databases address this by periodically writing data to disk.

3. **Cost**: RAM can be more expensive than traditional disk storage, so scaling up an in-memory database can be cost-prohibitive for large datasets.

In-memory data stores are commonly used for various applications, including real-time analytics, caching, session management, and high-frequency trading, where fast data access and low-latency responses are critical. Popular examples of in-memory data stores include Redis, Memcached, and various in-memory database systems.