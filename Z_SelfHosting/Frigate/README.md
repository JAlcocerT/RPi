# Frigate on Raspberry Pi (CSI camera)

Self-hosted NVR with motion-based recording for the Pi camera module, running entirely in Docker on a Pi 4/5 with 64-bit Debian (tested on Trixie).

## Architecture

```
[Pi CSI camera] -> mediamtx (host network, libcamera) -> RTSP :8654
                                                            |
                                                            v
                                                        Frigate (bridge net) -> UI :5000
```

- **mediamtx** uses its native `rpiCamera` source (libcamera under the hood) to grab the CSI camera and republish it as H264 RTSP. Runs in `network_mode: host` because libcamera needs direct access to `/dev` and `/run/udev`.
- **Frigate** consumes the RTSP stream over the host gateway (`host.docker.internal`), runs CPU-based detection at low fps, and records motion segments at full fps.

This split avoids the dead-end of trying to run libcamera *inside* the Frigate container — the Frigate image is Debian-based and does not ship libcamera or rpicam binaries, so `go2rtc exec:libcamera-vid` recipes you find online don't work out of the box.

## Files

- `docker-compose.yaml` — both services, `extra_hosts` maps `host.docker.internal` so the Frigate container can reach mediamtx on the host loopback.
- `mediamtx.yml` — Pi camera grabber config. RTSP on `:8654` (avoids collision with anything else on the default `:8554`, e.g. Home Assistant's go2rtc).
- `config/config.yml` — Frigate config. CPU detector, detect at 640x360@5fps, record 1280x720@15fps with motion-based 2-day retention, person tracking only.
- `storage/` — recordings/clips/exports. **Bind-mount this to a USB SSD before running long-term.** SD cards die fast under continuous video writes.

## Run

```bash
sudo docker compose pull
sudo docker compose up -d
sudo docker compose logs -f frigate
```

UI at `http://<pi-ip>:5000`. On first run Frigate auto-generates an `admin` password and prints it to the logs — capture it and change it in the UI.

## Stop / restart

```bash
sudo docker compose down
sudo docker compose up -d
```

## Gotchas we hit (in order)

### 1. Tailscale MagicDNS broke `docker pull`

Tailscale rewrites `/etc/resolv.conf` to point at `100.100.100.100`, and that resolver was intermittently failing to resolve external names like `ghcr.io`. Symptom:

```
failed to fetch anonymous token: ... lookup ghcr.io on 100.100.100.100:53: no such host
```

The `dns` field in `/etc/docker/daemon.json` only sets DNS *inside containers* — it does not affect the daemon's image-pull resolver, which uses the host's `/etc/resolv.conf`.

**Fix:** stop Tailscale from managing host DNS:

```bash
sudo tailscale set --accept-dns=false
```

NetworkManager will rewrite `/etc/resolv.conf` with the DHCP-provided resolver. If your router DNS is unreliable too (ours was), point at a public resolver:

```bash
echo -e "nameserver 1.1.1.1\nnameserver 8.8.8.8" | sudo tee /etc/resolv.conf
```

Trade-off: tailnet hostname resolution stops working (tailnet IPs still work). Re-enable with `sudo tailscale set --accept-dns=true` later if you need it, but the pull issue may return.

### 2. Frigate couldn't reach mediamtx on `127.0.0.1`

mediamtx binds `:8654` on the *host's* loopback (because `network_mode: host`). The Frigate container has its own loopback, so `rtsp://127.0.0.1:8654/picam` from inside Frigate is unreachable.

**Fix:** add the docker host gateway as a known hostname and reference it from `config.yml`:

```yaml
# docker-compose.yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

```yaml
# config/config.yml
path: rtsp://host.docker.internal:8654/picam
```

### 3. mediamtx port collision with existing go2rtc

If something else on the Pi (e.g., Home Assistant's go2rtc) already binds `:8554`, mediamtx must use a different port. We use `:8654` via `rtspAddress: :8654` in `mediamtx.yml`. Frigate's compose intentionally does NOT publish 8554/8555 externally for the same reason.

### 4. mediamtx config schema gotchas

The "disable transports" syntax depends on mediamtx version. On v1.18.x the keys are short forms like `rtmp: no`, `hls: no`, `webrtc: no`, `srt: no` — not `srtDisable`/`hlsDisable` (those crash with `json: unknown field`).

### 5. Frigate 0.17 record schema

The old `record.retain.{days,mode}` form was replaced in 0.17 by separate `continuous` and `motion` blocks:

```yaml
record:
  enabled: true
  continuous:
    days: 0
  motion:
    days: 2
```

A `version: 0.17-0` line at the bottom of `config.yml` is required.

### 6. `docker-compose` v3.x `version:` key

Modern Compose ignores it and warns. Removed.

## Verifying it's recording

```bash
sudo find storage/recordings -name "*.mp4" | head
sudo du -sh storage/recordings
```

Frigate writes ~10s mp4 segments continuously, then prunes by retention rule (we keep motion clips for 2 days, no continuous retention).

## Performance notes (Pi 4/5, no Coral)

- CPU detector is fine for a single camera at 5fps detect rate. Frigate itself warns this is "for testing only" — the warning is conservative; for one Pi camera it works.
- `ffmpeg.hwaccel_args: preset-rpi-64-h264` enables the Pi's hardware H264 decoder, which keeps CPU low.
- For more cameras or higher detect fps, add a Coral USB TPU and switch `detectors` to `edgetpu`. Plug into a USB 3.0 port.
- Tested camera: OV5647 (Pi Camera Module v1) at 1280x720@15fps. Newer modules (v2, v3, HQ) work the same — `mediamtx` picks them up via libcamera automatically.

## Things still to do

- [ ] Move `storage/` to a USB SSD bind mount.
- [ ] Change the admin password from the auto-generated one.
- [ ] Optional: enable MQTT in `config.yml` and wire to Home Assistant for notifications.
- [ ] Optional: add a Coral TPU and switch detector type.
