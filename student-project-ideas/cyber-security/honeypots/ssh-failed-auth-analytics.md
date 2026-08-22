# Failed SSH Attempts as a Student Dataset

Setup and analysis notes for a Debian GCE `e2-micro` instance. User: `nethu`.

---

## Part 1 — Unprivileged packet capture

Grant `tcpdump` to a non-admin user via Linux file capabilities rather than sudo.

### 1. Install tools and create the group

```bash
sudo apt install libcap2-bin        # provides setcap/getcap
sudo groupadd -f pcap
sudo usermod -aG pcap nethu
```

### 2. Lock the binary to the group, grant capabilities

```bash
sudo chgrp pcap /usr/bin/tcpdump
sudo chmod 750  /usr/bin/tcpdump
sudo setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump
getcap /usr/bin/tcpdump
```

Expected output:

```
/usr/bin/tcpdump cap_net_admin,cap_net_raw=eip
```

The `chmod 750` matters. `setcap` attaches the capability to the *file*, so
without it every user on the box gets packet capture. The `e` (effective) bit is
needed because tcpdump isn't capability-aware and won't raise the permitted set
itself.

### 3. Pick up the group

Log out and back in, or in the current shell:

```bash
newgrp pcap
id -nG              # should list pcap
tcpdump -i ens4 -c 5
```

On GCE the primary NIC is usually `ens4`, not `eth0`.

### 4. Survive package upgrades

Capabilities live in the file's xattrs and are wiped on reinstall or upgrade.

```bash
sudo tee /etc/apt/apt.conf.d/99tcpdump-setcap >/dev/null <<'EOF'
DPkg::Post-Invoke { "if [ -x /usr/bin/tcpdump ]; then chgrp pcap /usr/bin/tcpdump; chmod 750 /usr/bin/tcpdump; setcap cap_net_raw,cap_net_admin=eip /usr/bin/tcpdump; fi"; };
EOF
```

### Sudo alternative

`sudo visudo -f /etc/sudoers.d/tcpdump`:

```
nethu ALL=(root) NOPASSWD: /usr/bin/tcpdump
```

Simpler and logged, but tcpdump's `-z postrotate-command` flag makes this
equivalent to giving `nethu` full root. Only appropriate if that's already
acceptable. Argument restrictions in sudoers don't reliably help.

### e2-micro constraints

2 shared vCPU-fraction and 1 GB RAM. An unfiltered capture on a busy interface
drops packets and eats memory fast. Use a snaplen and rotating files:

```bash
tcpdump -i ens4 -s 128 -w /tmp/cap.pcap -C 50 -W 4 'port 443'
```

Debian ships an AppArmor profile for tcpdump that limits where it can write, so
`/tmp` or the user's home is safer than an arbitrary path.

---

## Part 2 — Widen what sshd records

Before analysing, get richer raw data. In `/etc/ssh/sshd_config`:

```
LogLevel VERBOSE
```

This adds the fingerprint of any public key a client offers — a strong botnet
identifier, since the same stolen key gets sprayed by whole bot families.

Sources worth pulling from separately:

- `/var/log/auth.log`
- `journalctl -u ssh` (doesn't always carry identical detail)
- `lastb` — the `btmp` binary log, structured, root-only

### Line types to parse as distinct classes

| Log line | Meaning |
|---|---|
| `Invalid user X from IP` | Username didn't exist at all |
| `Failed password for root` | Valid account — different threat class |
| `Connection closed by authenticating user` | Bot gave up mid-handshake |
| `Unable to negotiate ... no matching key exchange method` | Old or obscure client tooling |
| `banner exchange: ... invalid format` | Scanner, not an SSH client at all |

---

## Part 3 — Statistical angles

### Inter-arrival times

Test whether attempts form a Poisson process. Compute the Fano factor
(variance / mean of counts per fixed bin). It comes out far above 1 because
traffic is bursty — one bot hammering for 90 seconds, then hours of quiet. A
concrete demonstration of why the naive Poisson assumption fails on real network
data.

### Heavy tails

Rank IPs by attempt count, plot log-log, fit a power law. Compute a Gini
coefficient over sources. Typically a handful of IPs generate most of the volume
— which has a direct operational implication for how much a blocklist actually
buys you.

### Username analysis

- Shannon entropy of the username distribution, overall and per source IP.
- Pairwise Jaccard similarity between the username sets of different IPs. Bots
  sharing a wordlist cluster tightly, letting you group them into campaigns
  without knowing anything about the operators.
- **Ordering** is even stronger: if two IPs try usernames in the same sequence,
  they're running the same tool against the same dictionary file.

### Seasonality

Attempts by UTC hour-of-day and day-of-week. Some campaigns are cron-scheduled
and show sharp periodicity; botnets running on compromised residential hardware
track the diurnal cycle of their host region.

### Recidivism / survival analysis

For each IP, time between first and last sighting. Most appear once and vanish;
a small set persists for weeks. A Kaplan-Meier curve of "source lifetime" is a
legitimate use of survival methods on non-medical data.

---

## Part 4 — Tie it to the packet capture

This is where the tcpdump setup pays off. The SSH version banner and the full
key-exchange proposal are sent **in cleartext** before encryption starts, so a
pcap on port 22 gives you fields the logs never see.

- **Client version strings** — `SSH-2.0-libssh_0.9.6`, `SSH-2.0-Go`,
  `SSH-2.0-PUTTY_Release_0.70`. Tool fingerprinting.
- **HASSH fingerprints** — hash the ordered lists of KEX algorithms, ciphers,
  MACs and compression methods. The SSH analogue of JA3. Clustering by HASSH
  often separates botnet families more cleanly than IP or username does, and
  implementing it yourself from a pcap is a genuinely interesting project.
- **TCP-layer signals** — initial TTL and window size for passive OS
  fingerprinting; SYNs that never complete a handshake distinguish pure scanners
  from actual login attempts.

You only need the first few packets of each session:

```bash
tcpdump -i ens4 -s 512 -w /tmp/ssh.pcap \
  'tcp port 22 and (tcp[tcpflags] & tcp-syn != 0 or greater 100)'
```

---

## Part 5 — Enrichment

Map IPs to ASN using Team Cymru's whois interface — no API key needed:

```bash
whois -h whois.cymru.com " -v 1.2.3.4"
```

Then ask: what fraction come from cloud providers versus residential ISPs?
Cloud-origin attacks are rented infrastructure; residential ones are usually
compromised IoT.

Add MaxMind GeoLite2 for country. Cross-reference against free blocklists
(blocklist.de, Spamhaus DROP, AbuseIPDB free tier) and measure the **novelty
rate** — what percentage of your attackers were already publicly known at the
time you saw them? That's a meaningful finding about how useful threat feeds are
for a small operator.

---

## Part 6 — Interventions, not just observation

Observational stats are fine, but experiments make a much stronger write-up.

- **Port move.** Move sshd to a high port and measure the drop in attempt rate.
  Quantifies "security by obscurity" instead of arguing about it.
- **fail2ban.** Measure attempts before and after, plus estimated CPU and
  bandwidth saved. Use change-point detection (CUSUM or a simple Bayesian
  changepoint) on the time series rather than eyeballing it.
- **Tarpit.** Run `endlessh` on port 22 with real sshd elsewhere. It feeds bots
  an infinite banner; you measure how long each one hangs before disconnecting,
  which is a behavioural fingerprint in itself. Very light on a 1 GB box.
- **Honeypot.** Cowrie captures the actual passwords tried and what commands
  bots run post-"login" — the richest data by far, but Python-based and tight on
  an e2-micro's RAM. Run it in a separate throwaway VM if you can.

---

## Part 7 — Practical setup

Parse into SQLite and analyse with pandas. Weeks of auth logs are only a few
tens of MB, so the whole thing fits comfortably.

Suggested schema:

```sql
CREATE TABLE attempts (
  id         INTEGER PRIMARY KEY,
  ts         TEXT    NOT NULL,   -- ISO 8601, UTC
  source_ip  TEXT    NOT NULL,
  src_port   INTEGER,
  username   TEXT,
  auth_method TEXT,              -- password | publickey | none
  result     TEXT,               -- failed | invalid_user | closed | negotiate_fail
  key_fp     TEXT,               -- from LogLevel VERBOSE
  raw        TEXT
);
CREATE INDEX idx_ip ON attempts(source_ip);
CREATE INDEX idx_ts ON attempts(ts);
```

Run a nightly cron rollup. Set `logrotate` retention deliberately — the default
two weeks will silently destroy your history.

---

## Two cautions

**Don't scan or probe back at source IPs.** Besides being illegal in most
jurisdictions, it corrupts your own dataset.

**IP addresses are personal data under UK GDPR.** If you publish or share the
dataset, hash or truncate the addresses — keep the /24 for clustering, drop the
last octet.
