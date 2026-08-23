# tcpdump: watching port 2222

A short practical guide, built around `tcpdump -i ens4 port 2222` on a GCE instance.

## The command

```bash
tcpdump -i ens4 port 2222
```

| Part | Meaning |
| --- | --- |
| `-i ens4` | Capture on interface `ens4` (the primary NIC on most GCE Debian/Ubuntu images). Use `-D` to list interfaces, `-i any` for all of them, `-i lo` for loopback-only traffic. |
| `port 2222` | A BPF filter. Matches port 2222 as **either** source or destination, over **both** TCP and UDP. |

Everything after the flags is the filter expression. Narrow it as needed:

```bash
tcpdump -i ens4 tcp port 2222                    # TCP only
tcpdump -i ens4 dst port 2222                    # inbound to the port only
tcpdump -i ens4 'tcp port 2222 and not host 10.0.0.5'
tcpdump -i ens4 'port 2222 or port 22'
```

Quote expressions containing `(`, `)` or spaces so the shell doesn't mangle them.

### Flags worth adding

```bash
tcpdump -i ens4 -nn -c 50 tcp port 2222
```

- `-n` — don't resolve IPs to hostnames. `-nn` — also don't resolve port numbers to service names.
- `-c 50` — stop after 50 packets.
- `-q` — quiet, one short line per packet.
- `-t` / `-tttt` — no timestamp / full date-and-time timestamp.
- `-v`, `-vv`, `-vvv` — more protocol detail (TTL, IP ID, checksum validation).
- `-A` — print payload as ASCII. `-X` — hex plus ASCII.
- `-s 128` — snaplen: only store the first 128 bytes of each packet.
- `-w file.pcap` — write raw packets to a file for Wireshark. `-r file.pcap` to read one back.

**Use `-nn` by default.** In the sample output below, every line is dominated by
`sensor-01.us-central1-a.c.tcp-connectivity.internal` and
`host81-157-89-247.range81-157.btcentralplus.com`. Those are reverse-DNS lookups. They
make lines unreadable, they slow the capture down, and each lookup generates its own
network traffic from the box you are trying to observe.

### Safe long-running capture on a small VM

On an e2-micro, a forgotten capture can fill the boot disk. Use a ring buffer:

```bash
tcpdump -i ens4 -nn -s 128 -W 5 -C 50 -w /home/nethu/2222.pcap tcp port 2222
```

Five files of 50 MB maximum, oldest overwritten. Keep the filter as specific as you can —
filtering in BPF is far cheaper than filtering afterwards.

---

## Reading the output

### The header lines

```
tcpdump: verbose output suppressed, use -v[v]... for full protocol decode
listening on ens4, link-type EN10MB (Ethernet), snapshot length 262144 bytes
```

Not warnings — just tcpdump reporting how it started.

- **verbose output suppressed** — you get the default one-line summary per packet. Add
  `-v`, `-vv` or `-vvv` for deeper decoding. Nothing is being dropped, only not printed.
- **listening on ens4** — confirms the interface. If you expected traffic and see none,
  check this is the interface the traffic actually crosses.
- **link-type EN10MB (Ethernet)** — the layer-2 framing. `EN10MB` means standard Ethernet
  regardless of actual link speed; the name is historical. Loopback would show `LINUX_SLL`
  or `NULL`.
- **snapshot length 262144 bytes** — bytes captured per packet. The modern default is
  256 KB, i.e. effectively the whole packet. Lower it with `-s` when writing to disk.

On exit you also get a summary: packets *captured* (handed to tcpdump), *received by
filter*, and *dropped by kernel*. A non-zero drop count means the kernel buffer overflowed
and your capture has holes — tighten the filter or lower the snaplen.

### The anatomy of a packet line

```
15:30:59.473564 IP <src>.50419 > <dst>.2222: Flags [S], seq 2441130437, win 65535, options [...], length 0
```

| Field | Meaning |
| --- | --- |
| `15:30:59.473564` | Local time, microsecond resolution. |
| `IP` | IPv4. IPv6 shows as `IP6`. |
| `<host>.50419` | Source host and port. The port is the segment **after the last dot** — easy to miss when hostnames are being resolved. |
| `>` | Direction of travel. |
| `Flags [S]` | TCP flags — see below. |
| `seq` / `ack` | Sequence and acknowledgement numbers. |
| `win 65535` | Receive window the sender is advertising. |
| `options [...]` | TCP options from the header. |
| `length 0` | **Payload** bytes, not frame size. A pure ACK or SYN is `length 0`. |

### TCP flags

| Notation | Flag | Meaning |
| --- | --- | --- |
| `[S]` | SYN | Open a connection |
| `[S.]` | SYN-ACK | The `.` means ACK is also set |
| `[.]` | ACK | Pure acknowledgement, no data |
| `[P.]` | PSH-ACK | Carries payload, deliver it to the app now |
| `[F.]` | FIN-ACK | Graceful close of this direction |
| `[R]` | RST | Abrupt reset — abort the connection |

A trailing `.` on any of these just means the ACK bit is also set.

### Sequence numbers

The first packet of a flow shows the **absolute** initial sequence number
(`seq 2441130437`). After that, tcpdump prints numbers **relative** to that start, which
is why later packets show small values like `seq 1:42, ack 2`. Use `-S` to force absolute
numbers throughout.

`seq 1:42, ack 2` reads as: this segment carries bytes 1 up to (not including) 42 — 41
bytes — and acknowledges everything the peer has sent through byte 1.

### Common options

- `mss 1452` — largest payload the sender will accept. Client MSS 1452 implies a 1492-byte
  MTU (typical of PPPoE consumer broadband); server MSS 1420 implies GCE's 1460 MTU.
- `wscale 6` / `wscale 7` — window scale factor. Multiply `win` by 2^scale for the true
  window, so `win 506` with `wscale 7` is roughly 64 KB.
- `TS val ... ecr ...` — timestamps. `val` is the sender's clock, `ecr` echoes the last
  value seen from the peer. Subtracting them gives a rough RTT.
- `sackOK` — selective acknowledgement supported.
- `nop` — padding to keep options 4-byte aligned. Ignore it.
- `eol` — end of option list.

---

## Walking through the sample capture

Ten packets, two connections, from a BT broadband client in the UK to port 2222 on
`sensor-01` in `us-central1-a`.

### Connection 1 — client port 50419

**1. `.473564` client → server, `[S]`, seq 2441130437, win 65535**
The SYN. Client opens from ephemeral port 50419, offers MSS 1452, window scaling ×64,
SACK and timestamps.

**2. `.473622` server → client, `[S.]`, seq 797508644, ack 2441130438**
SYN-ACK, 58 microseconds later — the server's own kernel responding, so the delay is
just local processing. `ack` is the client's ISN + 1: "I have your SYN, send me byte 1."
Something *is* listening on 2222; a closed port would have produced `[R.]` instead.

**3. `.573692` client → server, `[.]`, ack 1**
The handshake's final ACK, 100 ms after the SYN-ACK. **That 100 ms is your round-trip
time** — the only true RTT measurement in this trace, and reasonable for UK to Iowa.
The connection is now established.

**4. `.576415` client → server, `[F.]`, seq 1, ack 1, length 0**
Three milliseconds later the client sends FIN having transmitted **zero bytes of data**.
It completed a handshake and immediately hung up. That is the signature of a port scanner
or a TCP connectivity check, not a real client — an SSH client would have waited for the
banner and replied with its own.

**5. `.579023` server → client, `[.]`, ack 2**
Server acknowledges the FIN. The `ack 2` counts the FIN as one byte.

**6. `.605510` server → client, `[P.]`, seq 1:42, length 41**
The server sends 41 bytes anyway — the length and timing are consistent with an SSH
version banner such as `SSH-2.0-OpenSSH_...`. This is legal: the client closed only *its*
direction (a half-close), so the server may still send. Note the 26 ms gap after the ACK,
which is the listening application waking up and writing its greeting.

**7. `.605633` server → client, `[F.]`, seq 42**
Server finishes and closes its side too.

**8–9. `.704960` and `.705379` client → server, `[R]`, win 0**
One RTT later, two resets. The client didn't half-close — it tore the socket down
completely. Data arriving for a socket that no longer exists gets a RST, and here there
were two arrivals to reject (the 41 bytes and the FIN), hence two resets. `win 0` and the
absolute sequence number are normal for a RST.

### Connection 2 — client port 50430

**10. `15:31:22.352443` client → server, `[S]`, seq 1922430436**
Twenty-three seconds later the same source host starts again from a **new** ephemeral
port, 50430. New port means a genuinely new connection, not a retransmission.

### What the trace tells you

- Port 2222 is open and a service is answering. If you are debugging "can anything reach
  my service?", the answer here is yes.
- The peer connects, completes the handshake, sends nothing, and disconnects — repeatedly,
  on a rough interval. Treat it as scanning or automated probing rather than real usage.
- Every full connection costs about 100 ms of RTT, which is what to expect from that
  client location.

To watch this pattern more readably:

```bash
tcpdump -i ens4 -nn -tttt 'tcp port 2222 and tcp[tcpflags] & tcp-syn != 0'
```

That prints only SYN and SYN-ACK packets — one or two lines per connection attempt —
which is usually the fastest way to see who is knocking.
