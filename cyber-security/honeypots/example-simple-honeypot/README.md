# Example: Simple Port Honeypot

A minimal, self-written honeypot — the "Approachable" option from the [project write-up](../README.md) that shows real coding skill: a TCP listener that logs every connection and every byte sent to it.

## What it does (and doesn't do)

`honeypot.py` binds to a port, sends a fake SSH banner, and logs:

- every connection (source IP, port, timestamp)
- every chunk of data a client sends (as hex and best-effort text)
- disconnects

It does **not** implement the real SSH protocol (no key exchange, no auth). That means it won't capture plaintext usernames/passwords the way Cowrie does — real SSH clients encrypt that exchange immediately after the banner. What you *do* get: connection metadata, timing, and raw payloads from bots/scanners that don't bother with a real handshake (surprisingly common). If you want captured credentials, layer this project up to Cowrie next, as the main write-up suggests.

## Run it locally (safe, no exposure)

```bash
pip install -r requirements.txt

# Terminal 1 — start the honeypot on a high, unprivileged port
python honeypot.py --port 8022 --log logs/honeypot.log

# Terminal 2 — simulate a "bot" connecting
printf 'hello world\n' | nc localhost 8022
```

Let it collect a few connections, then stop it with Ctrl+C.

## Analyze the logs

```bash
python analyze.py --log logs/honeypot.log --out logs
```

Prints a summary (total connections, unique IPs, first-seen time, top talkers) and writes two charts:

- `logs/top_ips.png` — bar chart of top source IPs
- `logs/timeline.png` — connections per hour

## Going further

- Point a real port (e.g. router port 22) at this script's port to see real internet bot traffic — only on infrastructure you own or are authorised to use, and only from an isolated host/VM (see the safety notes in the [main README](../README.md)).
- Add GeoIP lookup on `src_ip` for a map of attacker origins.
- Swap this script out for Cowrie once you want full SSH login/credential capture.
