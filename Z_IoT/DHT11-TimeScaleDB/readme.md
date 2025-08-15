
## DHT11 x TimeScale

Previously I was using the DHT11 with InfluxDB, was curious about adapting that project to accept the TimescaleBD as well.


**Data to Pin7 - GPIO4**

5v
gnd



```sh
docker build -t dht_sensor_timescale .
```



Checking the data ingestion: 


docker run -it --rm --network=dht_timescaledb_app_network postgres psql -h timescaledb_container -U myuser -d mydb --username=myuser


```sql
SELECT * FROM dht_sensor;
SELECT MAX(temperature) FROM dht_sensor;
```


list the databases available

\l

If you want to list all tables and their associated schemas, you can use:



\dt


See the schema of the table:

\d+ dht_sensor