```sh
docker run -d --name timescaledb \
    -e POSTGRES_USER=pico \
    -e POSTGRES_PASSWORD=pico \
    -e POSTGRES_DB=sensors \
    -p 5432:5432 \
    timescale/timescaledb:latest-pg16
```