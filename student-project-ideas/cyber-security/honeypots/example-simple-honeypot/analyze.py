#!/usr/bin/env python3
"""Parse honeypot.py's JSONL log and produce summary stats + charts.

Usage:
    python analyze.py --log logs/honeypot.log --out logs
"""

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

import matplotlib.pyplot as plt


def load_events(log_path: Path) -> list[dict]:
    events = []
    with log_path.open() as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def summarize(events: list[dict]) -> None:
    connects = [e for e in events if e["event"] == "connect"]
    data_events = [e for e in events if e["event"] == "data"]

    ip_counts = Counter(e["src_ip"] for e in connects)

    print(f"Total connections: {len(connects)}")
    print(f"Unique source IPs: {len(ip_counts)}")
    print(f"Data-carrying packets captured: {len(data_events)}")
    if connects:
        first_seen = datetime.fromtimestamp(min(e["timestamp"] for e in connects), tz=timezone.utc)
        print(f"First connection: {first_seen.isoformat()}")

    print("\nTop 10 source IPs:")
    for ip, count in ip_counts.most_common(10):
        print(f"  {ip:<20} {count}")


def plot_top_ips(events: list[dict], out_path: Path) -> None:
    connects = [e for e in events if e["event"] == "connect"]
    ip_counts = Counter(e["src_ip"] for e in connects)
    top = ip_counts.most_common(10)
    if not top:
        return

    ips, counts = zip(*top)
    plt.figure(figsize=(8, 5))
    plt.barh(ips[::-1], counts[::-1])
    plt.xlabel("Connections")
    plt.title("Top source IPs")
    plt.tight_layout()
    plt.savefig(out_path / "top_ips.png")
    plt.close()


def plot_timeline(events: list[dict], out_path: Path) -> None:
    connects = [e for e in events if e["event"] == "connect"]
    if not connects:
        return

    hours = Counter(
        datetime.fromtimestamp(e["timestamp"], tz=timezone.utc).strftime("%Y-%m-%d %H:00")
        for e in connects
    )
    labels = sorted(hours)
    counts = [hours[label] for label in labels]

    plt.figure(figsize=(10, 5))
    plt.plot(labels, counts, marker="o")
    plt.xticks(rotation=45, ha="right")
    plt.ylabel("Connections")
    plt.title("Attack timeline (connections per hour, UTC)")
    plt.tight_layout()
    plt.savefig(out_path / "timeline.png")
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log", default="logs/honeypot.log")
    parser.add_argument("--out", default="logs")
    args = parser.parse_args()

    log_path = Path(args.log)
    out_path = Path(args.out)
    out_path.mkdir(parents=True, exist_ok=True)

    if not log_path.exists() or log_path.stat().st_size == 0:
        print(f"No events found in {log_path}. Run honeypot.py first and generate some traffic.")
    else:
        events = load_events(log_path)
        summarize(events)
        plot_top_ips(events, out_path)
        plot_timeline(events, out_path)
        print(f"\nCharts written to {out_path}/top_ips.png and {out_path}/timeline.png")
