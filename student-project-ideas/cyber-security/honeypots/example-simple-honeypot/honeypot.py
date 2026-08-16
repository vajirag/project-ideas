#!/usr/bin/env python3
"""A minimal TCP port honeypot.

Listens on a port, sends a fake banner, and logs every connection and
every byte a client sends — nothing more. It does not implement the real
SSH/Telnet protocol, so it won't capture plaintext credentials the way
Cowrie does; what it's good for is connection metadata (who connects, how
often, how fast) and raw payloads from simpler bots/scanners.
"""

import argparse
import asyncio
import json
import time
from pathlib import Path

BANNER = b"SSH-2.0-OpenSSH_7.4\r\n"
READ_TIMEOUT_SECONDS = 5
MAX_READ_BYTES = 4096


def log_event(log_path: Path, event: dict) -> None:
    event["timestamp"] = time.time()
    with log_path.open("a") as f:
        f.write(json.dumps(event) + "\n")


async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, log_path: Path) -> None:
    peer_ip, peer_port = writer.get_extra_info("peername")[:2]
    log_event(log_path, {"event": "connect", "src_ip": peer_ip, "src_port": peer_port})
    print(f"[+] connection from {peer_ip}:{peer_port}")

    try:
        writer.write(BANNER)
        await writer.drain()

        while True:
            try:
                data = await asyncio.wait_for(reader.read(MAX_READ_BYTES), timeout=READ_TIMEOUT_SECONDS)
            except asyncio.TimeoutError:
                break
            if not data:
                break
            log_event(
                log_path,
                {
                    "event": "data",
                    "src_ip": peer_ip,
                    "src_port": peer_port,
                    "data_hex": data.hex(),
                    "data_repr": data.decode("utf-8", errors="replace"),
                },
            )
    finally:
        log_event(log_path, {"event": "disconnect", "src_ip": peer_ip, "src_port": peer_port})
        print(f"[-] disconnected {peer_ip}:{peer_port}")
        writer.close()


async def main(host: str, port: int, log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, log_path), host, port)
    print(f"Honeypot listening on {host}:{port} — logging to {log_path}")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=2222)
    parser.add_argument("--log", default="logs/honeypot.log")
    args = parser.parse_args()

    try:
        asyncio.run(main(args.host, args.port, Path(args.log)))
    except KeyboardInterrupt:
        print("\nShutting down.")
