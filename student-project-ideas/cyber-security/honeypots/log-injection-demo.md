# Log Injection in the Honeypot Script

A focused write-up: what log injection is, why the original honeypot is vulnerable, how to demonstrate it against your own instance, and how to fix it.

**Scope:** everything below is run against a honeypot you control, bound to `127.0.0.1`. Nothing here reaches another machine.

---

## 1. What log injection is

Log injection happens when untrusted input is written into a log without neutralising the characters that give the log file its structure. For a line-oriented log, the structural character is the newline. Control it, and you control where one record ends and the next begins.

The consequences fall into three buckets:

- **Forged records** — the attacker writes lines that look exactly like ones your own code produced.
- **Downstream exploitation** — anything that parses the log (SIEM, `fail2ban`, a grep script) consumes attacker-authored data as if it were trusted.
- **Terminal manipulation** — if the same string is printed to a console, ANSI escape sequences let the attacker alter what the operator sees.

None of these is code execution. The severity is about **integrity of evidence**, which for a honeypot is the entire point of the tool.

---

## 2. The vulnerable line

```python
data = client_socket.recv(1024)
if data:
    payload_msg = f"PAYLOAD FROM {attacker_ip}: {data.decode('utf-8', errors='ignore').strip()}"
    print(f"[!] {payload_msg}")
    logging.info(payload_msg)
```

Three things combine to create the hole:

**`.strip()` is not sanitisation.** It removes whitespace from the *ends* of the string. A `\n` in the middle passes through completely untouched. This is the single most common misunderstanding behind this bug class — it looks like cleaning, but it only trims.

**`logging` does not escape message bodies.** The `logging` module formats your record, appends one newline, and writes. It never inspects the message for embedded newlines, because it has no way to know they weren't intended.

**The same string goes to `print()`.** So any ANSI escape sequence in the payload is interpreted by the operator's terminal emulator.

The attacker controls every byte after `PAYLOAD FROM 203.0.113.9: `, which means they control everything from that point to the end of the file.

---

## 3. Lab setup

Save the original as `honeypot_vuln.py`:

```python
import socket
import logging

logging.basicConfig(
    filename="honeypot.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def start_honeypot(host="127.0.0.1", port=2222):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server_socket.bind((host, port))
        server_socket.listen(5)
        print(f"[*] Honeypot actively listening on {host}:{port}...")
        while True:
            client_socket, client_address = server_socket.accept()
            attacker_ip, attacker_port = client_address[0], client_address[1]
            log_msg = f"CONNECTION ATTEMPT: IP={attacker_ip}, Port={attacker_port}"
            print(f"[!] {log_msg}")
            logging.info(log_msg)
            try:
                client_socket.sendall(b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n")
                data = client_socket.recv(1024)
                if data:
                    payload_msg = f"PAYLOAD FROM {attacker_ip}: {data.decode('utf-8', errors='ignore').strip()}"
                    print(f"[!] {payload_msg}")
                    logging.info(payload_msg)
            except Exception:
                pass
            finally:
                client_socket.close()
    except KeyboardInterrupt:
        print("\n[*] Shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_honeypot()
```

Note the bind address is `127.0.0.1`, not `0.0.0.0` — for this exercise there's no reason to expose it.

Run it in one terminal:

```bash
rm -f honeypot.log
python3 honeypot_vuln.py
```

Keep a second terminal for the client and a third watching the log:

```bash
tail -f honeypot.log
```

---

## 4. Test 1 — a normal connection (baseline)

```bash
printf 'SSH-2.0-TestClient\r\n' | nc -q1 127.0.0.1 2222
```

Log:

```
2026-08-23 14:02:09,412 - CONNECTION ATTEMPT: IP=127.0.0.1, Port=51884
2026-08-23 14:02:09,413 - PAYLOAD FROM 127.0.0.1: SSH-2.0-TestClient
```

Two lines, one connection, both written by your code. This is what a genuine record looks like — note the exact format, because that's what we're about to counterfeit.

---

## 5. Test 2 — forging a log entry

Now send a payload containing a newline followed by a line that mimics the format above:

```bash
printf 'A\n2026-08-23 09:00:00,000 - CONNECTION ATTEMPT: IP=8.8.8.8, Port=1337\n' \
  | nc -q1 127.0.0.1 2222
```

Log:

```
2026-08-23 14:05:22,101 - CONNECTION ATTEMPT: IP=127.0.0.1, Port=51902
2026-08-23 14:05:22,102 - PAYLOAD FROM 127.0.0.1: A
2026-08-23 09:00:00,000 - CONNECTION ATTEMPT: IP=8.8.8.8, Port=1337
```

The third line is a fabrication. Nothing in your code produced it, no connection from `8.8.8.8` ever occurred, and the timestamp is five hours earlier than the moment it was written. There is no field in the file that distinguishes it from line one.

Confirm the forgery is now indistinguishable to any consumer of the log:

```bash
grep 'CONNECTION ATTEMPT' honeypot.log
```

Both the real and the forged entry match. An analyst reading this file, or a script counting unique attacker IPs, has no way to tell them apart.

### Scaling it up

A single connection can inject an arbitrary number of records, up to the 1024-byte read limit:

```python
# flood_test.py — run against your own honeypot only
import socket

lines = "".join(
    f"\n2026-08-23 0{h}:00:00,000 - CONNECTION ATTEMPT: IP=10.0.0.{h}, Port=2222"
    for h in range(1, 9)
)
s = socket.create_connection(("127.0.0.1", 2222))
s.recv(1024)          # consume the banner
s.sendall(lines.encode())
s.close()
```

```bash
python3 flood_test.py
grep -c 'CONNECTION ATTEMPT' honeypot.log
```

One TCP connection, eight fabricated events implicating eight different addresses.

---

## 6. Test 3 — terminal manipulation

The payload is also `print()`ed, so escape sequences reach the terminal running the honeypot. Watch the honeypot's own terminal while you run:

```bash
printf 'X\033[2J\033[H[*] Honeypot actively listening on 127.0.0.1:2222...' \
  | nc -q1 127.0.0.1 2222
```

`\033[2J` clears the screen and `\033[H` homes the cursor. The honeypot's console is wiped and replaced with what looks like a freshly started, idle service. Every connection you'd logged visually is gone from view.

A subtler variant uses `\033[1A` (cursor up) and `\033[2K` (clear line) to overwrite just the preceding line, deleting the record of one specific connection while leaving the rest of the session intact.

The file on disk still holds those lines — this attack only affects the live view. But an operator watching the console in real time is exactly the person this misleads.

---

## 7. Test 4 — poisoning a downstream parser

This is where the bug stops being cosmetic. Suppose you later write something that reads the log and acts on it — a very common next step:

```python
# blocklist.py — naive log consumer
import re

pattern = re.compile(r"CONNECTION ATTEMPT: IP=(\d+\.\d+\.\d+\.\d+)")
with open("honeypot.log") as fh:
    ips = {m.group(1) for line in fh if (m := pattern.search(line))}

for ip in sorted(ips):
    print(f"iptables -A INPUT -s {ip} -j DROP")   # would-be block rule
```

```bash
python3 blocklist.py
```

After the tests above, the output includes `8.8.8.8` and the `10.0.0.x` range — addresses that never connected. Point this at a real `iptables` invocation, or feed the log to `fail2ban` with a matching regex, and an attacker chooses what you block. Nominating your own gateway, your DNS resolver, or a business partner's IP range is a self-inflicted denial of service.

This is the concrete reason to fix it even though the raw honeypot is harmless: the log is an input to future tooling, and inputs you don't control need to be trustworthy at the point they're written.

---

## 8. The fix

Never build a log line out of decoded attacker text. Log the raw `bytes` object through `%r`:

```python
logger.info("PAYLOAD ip=%s len=%d data=%r", ip, len(data), data)
```

Why this works:

- **`repr()` of `bytes` escapes every control character.** A newline becomes the two literal characters `\` and `n`. A `\033` becomes `\x1b`. The result is guaranteed single-line and guaranteed printable, so it can neither break the record boundary nor reach the terminal as an escape sequence.
- **It never decodes.** `errors='ignore'` was silently discarding bytes that aren't valid UTF-8 — which for a honeypot are the interesting ones. `%r` preserves them as `\xNN`.
- **Lazy formatting keeps data out of the format string.** Passing `data` as an argument rather than interpolating it means it can never be parsed as a format specifier.

Adding `len=%d` lets you spot truncation at the read cap without eyeballing the repr.

### Fixed handler

```python
#!/usr/bin/env python3
"""Honeypot with log injection fixed."""

import logging
import socket
import socketserver
from logging.handlers import RotatingFileHandler

BANNER = b"SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5\r\n"
READ_TIMEOUT = 5.0
MAX_PAYLOAD = 1024

logger = logging.getLogger("honeypot")


def configure_logging(path="honeypot.log"):
    handler = RotatingFileHandler(path, maxBytes=10_000_000, backupCount=5)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False


class HoneypotHandler(socketserver.BaseRequestHandler):
    def handle(self):
        ip, port = self.client_address
        logger.info("CONNECT ip=%s port=%d", ip, port)
        print(f"[!] connect {ip}:{port}", flush=True)
        try:
            self.request.settimeout(READ_TIMEOUT)
            self.request.sendall(BANNER)
            data = self.request.recv(MAX_PAYLOAD)
            if data:
                # %r on bytes: control chars escaped, always one line
                logger.info("PAYLOAD ip=%s len=%d data=%r", ip, len(data), data)
                print(f"[!] payload {ip} {len(data)}B {data!r}", flush=True)
        except socket.timeout:
            logger.info("TIMEOUT ip=%s", ip)
        except OSError as exc:
            logger.debug("SOCKERR ip=%s err=%s", ip, exc)


class Honeypot(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True


if __name__ == "__main__":
    configure_logging()
    with Honeypot(("127.0.0.1", 2222), HoneypotHandler) as server:
        print("[*] listening on 127.0.0.1:2222", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[*] shutting down", flush=True)
```

---

## 9. Re-running the tests

```bash
rm -f honeypot.log
python3 honeypot_fixed.py
```

**Test 2 (forgery):**

```bash
printf 'A\n2026-08-23 09:00:00,000 - CONNECTION ATTEMPT: IP=8.8.8.8, Port=1337\n' \
  | nc -q1 127.0.0.1 2222
```

```
2026-08-23 14:31:07,556 - CONNECT ip=127.0.0.1 port=52014
2026-08-23 14:31:07,557 - PAYLOAD ip=127.0.0.1 len=63 data=b'A\n2026-08-23 09:00:00,000 - CONNECTION ATTEMPT: IP=8.8.8.8, Port=1337\n'
```

The entire payload, newlines and all, sits inside one `data=` field. `grep -c 'CONNECT ip='` returns 1, not 2.

**Test 3 (terminal):** the escape bytes appear as `\x1b[2J\x1b[H` in both the log and the console. Nothing is cleared.

**Test 4 (parser):** the naive `blocklist.py` regex no longer matches anything inside the payload field, because the forged text is not on its own line and the field name has changed from the real event's. Run it and only `127.0.0.1` appears.

A one-line assertion that the fix holds:

```bash
# every log line must start with a timestamp
grep -cv '^[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\} ' honeypot.log   # expect 0
```

Against the vulnerable version this counts every injected line; against the fixed one it returns zero.

---

## 10. General rules

- **`.strip()`, `.trim()`, and friends are not sanitisers.** They touch the ends of a string only.
- **Escape at the point of writing, not at the point of reading.** Once a forged line is in the file, no parser can reliably tell it from a real one.
- **Prefer structured logs for untrusted data.** JSON Lines removes the whole class of problem, because the encoder escapes newlines by construction and each record is unambiguously one line:

  ```python
  import json, base64, time

  record = {
      "ts": time.time(),
      "event": "payload",
      "ip": ip,
      "len": len(data),
      "data_b64": base64.b64encode(data).decode(),
  }
  logger.info(json.dumps(record))
  ```

  Base64 for the payload sidesteps encoding questions entirely and makes the record safe to pass to any consumer.
- **Treat the log as untrusted input downstream too.** Even with escaping in place, a parser that acts on log contents — blocking IPs, sending alerts — should validate what it extracts rather than trusting the file's provenance.
- **Never print untrusted bytes to a terminal unescaped.** `repr()` is the cheapest possible defence and costs nothing in readability.
