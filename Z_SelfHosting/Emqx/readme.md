


```Dockerfile
FROM erlang:latest

# Set working directory
WORKDIR /app

# Copy your Erlang application code into the container
COPY . /app

# Install any additional dependencies or packages if needed
RUN apt-get update && apt-get install -y <package-name>

# Run your Erlang application
CMD ["erl"]
```

```sh
docker build -t my-erlang-app .
```