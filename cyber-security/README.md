# Cyber Security Projects

Summer project ideas aimed at UK students (~16 years old). Each is self-contained, legal, safe to run without any real infrastructure at risk, and produces a genuine written report with data/visualisations — not just "I got it working."

- **[Honeypots](honeypots/)** — deploy a decoy system, let real attackers find it, and analyse what they do. Defensive: you watch, you don't touch.
- **[Vulnerable Web App Pentest Lab](web-vuln-lab/)** — deploy a deliberately broken app in an isolated sandbox and attack it yourself with real pentesting tools. Offensive, but entirely self-contained and legal.
- **[Phishing Email Detector](phishing-detector/)** — build a classifier that flags phishing indicators using public research datasets. Data-analysis-meets-security, fully passive/read-only.
- **[Home Network Security Audit](home-network-audit/)** — inventory and audit your own home network with Nmap and Wireshark; find and fix what's unencrypted or still on default settings.
- **[Build Your Own 2FA (TOTP) Generator](totp-generator/)** — implement the algorithm behind Google Authenticator/Authy from the RFC, from first principles. Applied cryptography, tightly scoped.
- **[Digital Footprint / OSINT Audit](osint-footprint-audit/)** — run a passive open-source-intelligence investigation on yourself to see what's publicly discoverable, then lock it down.

All follow the same shape: research & threat model → build/set up → collect or gather data → analyse & visualise → write up & reflect. Pick based on what you want to practise: watching attackers (Honeypots), being the attacker against your own lab (Pentest Lab), working with data (Phishing Detector), networking fundamentals (Home Network Audit), applied cryptography (TOTP Generator), or recon/privacy (OSINT Audit).

## Advanced track

- **[Project Advance](advance/)** — kernel internals, sandboxing/isolation, memory safety & exploitation, observability, and boot integrity. A step up from the projects above: expect these to take longer than a week and to require comfort with C and Linux internals. Always done in a disposable VM.

## Resources

- **[RESOURCES.md](RESOURCES.md)** — hands-on platforms, reading, video, UK student programmes (CyberFirst), and community — grouped by purpose, with a recommended starting pair.
