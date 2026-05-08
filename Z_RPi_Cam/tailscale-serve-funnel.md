# Tailscale Serve & Funnel

HTTPS for homelab services without running a reverse proxy or opening router ports.

## TL;DR

| Feature | Reachable from | Use case |
|---|---|---|
| `tailscale serve` | Your tailnet only (devices logged into your Tailscale account) | Private dashboards, internal tools |
| `tailscale funnel` | Public internet (anyone with the URL) | Webhooks, public-facing demos, sharing |

Both give you free TLS certs (Let's Encrypt via Tailscale's MagicDNS) on `<machine>.<tailnet>.ts.net` — no DNS config, no certbot, no Nginx/Caddy/Traefik needed.

## Prerequisites

1. Tailscale installed + logged in (`tailscale up`).
2. MagicDNS enabled in admin panel (`https://login.tailscale.com/admin/dns`) — usually on by default.
3. HTTPS certificates enabled (admin panel → DNS → "Enable HTTPS").
4. For Funnel only: Funnel enabled in admin panel ACLs (`https://login.tailscale.com/admin/settings/funnel`).

Check ready state:

```bash
tailscale status
tailscale cert <hostname>.<tailnet>.ts.net   # forces cert provision
```

## tailscale serve — Private HTTPS

Forwards a tailnet HTTPS request to a local service.

### Examples

```bash
# Expose Portainer (running on :9000) at https://rpi.<tailnet>.ts.net
tailscale serve --bg 9000

# Expose under a path
tailscale serve --bg --set-path=/portainer http://localhost:9000

# Multiple services on one host (different ports)
tailscale serve --bg --https=8443 9000   # https://rpi.<tailnet>.ts.net:8443

# Static files
tailscale serve --bg / /var/www/html

# TCP forward (e.g. Postgres)
tailscale serve --bg --tcp=5432 tcp://localhost:5432
```

### Manage

```bash
tailscale serve status           # what's currently served
tailscale serve --bg=false 9000  # stop foreground
tailscale serve reset            # nuke all serve config
```

### Persistence

`--bg` runs in background and persists across reboots. State stored in `/var/lib/tailscale`.

## tailscale funnel — Public HTTPS

Same as serve, but exposes to the public internet via Tailscale's edge.

```bash
# First, enable funnel for the node (requires admin ACL)
tailscale funnel --bg 9000   # https://rpi.<tailnet>.ts.net publicly reachable
tailscale funnel status
tailscale funnel --bg=false 9000  # stop
tailscale funnel reset
```

### Restrictions

- Only ports 443, 8443, 10000 work for ingress (Tailscale-imposed).
- Must be enabled per-node in admin ACLs:
  ```json
  {
    "nodeAttrs": [
      { "target": ["tag:funnel-ok"], "attr": ["funnel"] }
    ]
  }
  ```
- Hostname always `<machine>.<tailnet>.ts.net` — can't use custom domain (yet).
- No path-level auth — funneled service is fully public unless service itself authenticates.

## RPi Homelab Use Cases

| Service | Recommended | Reason |
|---|---|---|
| Portainer | serve | Admin panel — never expose publicly |
| Frigate (NVR) | serve | Camera feeds — private only |
| Home Assistant | serve | Full home automation control |
| Grafana (internal metrics) | serve | Sensitive system data |
| Webhook receiver (GitHub, Stripe) | funnel | Needs public reachability |
| Public status page | funnel | Read-only public info |
| File share (one-off send) | funnel | Temporary public link |

## vs. Traditional Reverse Proxy

| Aspect | tailscale serve/funnel | Caddy / Traefik / Nginx |
|---|---|---|
| TLS cert | Auto, free | Auto (Caddy) or manual |
| Public DNS | Not needed | Required for funnel-equivalent |
| Router port-forward | Never | Needed for public access |
| Multi-domain | No (one ts.net hostname) | Yes |
| Auth middleware | No | Yes (basic auth, OAuth proxy, etc.) |
| Path routing | Limited | Full regex |
| Setup complexity | One command | Config file + DNS + certs |

**Pattern:** use `tailscale serve` for everything internal. Run Caddy behind it only if you need custom domain or auth middleware. Skip funnel unless something genuinely needs to be public.

## Gotchas

- **Cert provision lag:** first request after `tailscale serve` may take 10–30s while cert mints.
- **Funnel rate limits:** Tailscale enforces undocumented limits on funnel traffic. Don't host high-traffic public sites.
- **Single node only:** serve/funnel binds to the one machine. No HA.
- **`--bg` state lost on `tailscale logout`:** logging out clears all serve config.
- **Plan limits:** free plan = 3 funnel-enabled nodes. Personal plan = more.
- **No WebSocket buffering:** if your service streams (Frigate live view, Home Assistant), works fine but goes through Tailscale's edge — may add latency.
- **IPv6:** funnel ingress is IPv4 + IPv6. Some clients on IPv6-only networks may behave differently.

## Quick Setup Snippet for Script

```bash
enable_tailscale_serve_portainer() {
    if ! command_exists tailscale; then
        log "Tailscale not installed, skipping serve setup"
        return 0
    fi

    if ! tailscale status >/dev/null 2>&1; then
        log "Tailscale not logged in. Run 'tailscale up' first."
        return 0
    fi

    log "Configuring tailscale serve for Portainer (port 9000)..."
    tailscale serve --bg 9000 || log "Warning: serve config failed"
    tailscale serve status
}
```

## References

- Official: https://tailscale.com/kb/1242/tailscale-serve
- Funnel: https://tailscale.com/kb/1223/funnel
- ACL nodeAttrs: https://tailscale.com/kb/1337/acl-syntax#nodeattrs
