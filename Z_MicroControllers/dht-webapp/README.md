Here's what changed vs the old picow-dht-webapp:

  mqtt_to_db.py — subscribes to both pico/# and esp32/# instead of just pico/#. No     
  other changes needed since the DB stores any topic generically.

  main.py — added /history?hours=1&sensor=all REST endpoint that queries TimescaleDB   
  with time_bucket (auto-sized: 1min / 5min / 15min / 1h depending on range).
  Connection pool instead of a single connection.

  index.html — full redesign:
  - Sensor pills: All / Pico W / ESP32 — filters both cards and chart datasets
  - Range pills: 1h / 6h / 24h / 7d — re-fetches bucketed history
  - 4 cards (Pico W temp+humi, ESP32 temp+humi) with greyed-out state when filtered    
  - Two separate charts: Temperature (orange = Pico W, red = ESP32) and Humidity (blue 
  = Pico W, green = ESP32)
  - Charts refresh every 30s automatically; cards update live via WebSocket

  To deploy on the server, copy the three files and run the same way as before:        

  # terminal 1 — MQTT subscriber (stop old one if still running)
  tmux new-session -d -s mqtt-sub 'cd ~/dht-webapp && uv run mqtt_to_db.py'

  # terminal 2 — web app
  tmux new-session -d -s webapp 'cd ~/dht-webapp && uv run uvicorn main:app --host     
  0.0.0.0 --port 8077'