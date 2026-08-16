# Project: Home Network Security Audit

Before you can defend a network, you need to know what's actually on it. This project turns your own home network into the subject of a real security audit — capturing traffic, inventorying devices, and finding the default-password smart plug you forgot was even online.

## What this is (framing for the write-up)

A hands-on audit of a real, live network you're authorised to test — your own. You'll build an inventory of every device on the network, see what protocols they speak, and flag what's unencrypted, outdated, or still on factory defaults. It's the same first step a professional network security assessment starts with, done on infrastructure you already own.

## Approach by difficulty

### Approachable

- **Device inventory** — use `nmap -sn` (or your router's admin page) to list every device on the network, then `nmap -sV` against each to fingerprint what services/versions they're running.
- **Traffic capture** — run Wireshark for an hour while you use the network normally, and look at what protocols show up (DNS, HTTP vs HTTPS, mDNS, UPnP broadcasts).

### More ambitious

- **Unencrypted traffic hunt** — filter your Wireshark capture for plaintext HTTP, Telnet, or FTP traffic — anything sending data (including credentials) unencrypted.
- **IoT device review** — for every smart device you find, check: is it still on its default admin password? Is it running outdated firmware? Does it phone home to unexpected destinations (check its DNS queries)?
- **Router/Wi-Fi hardening review** — check your router's admin panel: WPA3 vs WPA2, WPS enabled (a common weak point), default admin credentials, remote management exposure.

## The analysis

- How many devices are actually on your network — did the count surprise you?
- What fraction of traffic is encrypted vs plaintext?
- Which devices are running outdated software or default credentials?
- What's the single biggest risk you found, and what's the fix?

Turn it into a proper audit report: a device inventory table (device, IP, open ports, risk level), a protocol breakdown chart (encrypted vs unencrypted traffic by volume), and a prioritised list of fixes.

## Safety notes that also read as maturity

- Only scan and capture traffic on **your own network**, with the household's awareness if other people's devices/traffic will be captured — Wireshark on a shared network sees everyone's traffic, not just yours.
- Using Nmap or any scanning tool against a network you don't own or don't have permission to test is illegal in the UK under the **Computer Misuse Act 1990** — stay entirely within your own home network.
- If you find a genuinely exposed device (e.g. a webcam with a default password reachable from the internet), fix it as part of the project — that's a better ending than just noting it.
- Don't publish your home network's real IP ranges, device serial numbers, or anything else identifying in a public write-up; redact before sharing.

**The single best insight to end on:** most home network risk isn't exotic — it's the ordinary stuff nobody got around to changing: a default password, an unpatched firmware, a device sending data in the clear. Finding and fixing that is more valuable than any single clever exploit, and it's a genuinely mature thing to have actually done rather than just read about.

## The week at a glance

1. **Research & scope** — read up on home network basics (what's a typical topology, what's normal vs suspicious traffic), confirm you have permission from anyone else on the network.
2. **Device inventory** — scan the network, list every device and what it's running.
3. **Capture traffic** — run Wireshark during normal use, save the capture for analysis.
4. **Analyse the capture** — filter for plaintext protocols, unexpected destinations, unusual volume.
5. **Review each device** — check for default credentials, outdated firmware, unnecessary exposed services.
6. **Fix what you can** — change default passwords, update firmware, disable unused services (WPS, remote admin, etc.).
7. **Write up & reflect** — audit report with inventory table, protocol chart, prioritised fix list.
