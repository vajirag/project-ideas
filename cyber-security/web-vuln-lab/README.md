# Project: Vulnerable Web App Pentest Lab

The offensive counterpart to [Honeypots](../honeypots/README.md): instead of waiting for attackers to come to you, you attack a target yourself — one that's deliberately built to be broken, running entirely on your own machine. No real target, no legal grey area, and the write-up reads like a genuine penetration-test report.

## What this is (framing for the write-up)

A deliberately vulnerable web application, deployed in an isolated sandbox, that you attack using the same tools and techniques real penetration testers use. The vulnerabilities are known and intentional — the skill being tested is finding them, exploiting them, and explaining how you'd fix them.

The "I broke it, and here's how I'd fix it" narrative is what turns this from "I hacked something" into a security project — the fix write-up is the part that shows real understanding.

## Targets by difficulty

### Approachable

- **OWASP Juice Shop** — a modern (Node.js) app deliberately riddled with vulnerabilities, with a built-in scoreboard that tracks which challenges you've solved as you find each one. Great for self-paced progress tracking.
- **DVWA (Damn Vulnerable Web Application)** — a classic PHP app where the *same* vulnerability (SQLi, XSS, etc.) is adjustable across low/medium/high difficulty — good for showing "here's the naive version, here's the hardened version" side by side.

### More ambitious

- **Metasploitable 2/3** — a full vulnerable VM with multiple services, not just web (FTP, SMB, misconfigured databases), for practising beyond web-only attacks.
- **OWASP WebGoat** — lesson-structured vulnerable app with guided challenges, useful if you want more scaffolding than Juice Shop/DVWA provide.

## The analysis

The exploit is only half the project — the value is in the report:

- What vulnerability did you find, and which OWASP Top 10 category does it fall under?
- How severe is it (what could an attacker actually do with it)?
- What request/payload triggered it — evidence, not just "it worked"?
- **How would you fix it?** (parameterised queries, output encoding, proper auth checks, etc.) — this is the step that separates a security project from just "I broke an app."
- If using DVWA's difficulty levels: what changed between low and high difficulty, and why does that change defeat the naive attack?

Turn it into visualisations — a table of findings by OWASP category and severity, a bar chart of vulnerability types found, a before/after comparison across difficulty levels.

## Safety notes that also read as maturity

- Run the vulnerable app entirely inside an isolated VM or Docker network with **no ports exposed to the internet** — it is deliberately full of holes and must never be reachable from outside your machine.
- Never point Nmap, ZAP, Burp Suite, or any scanning/exploitation tool at a system you don't own or don't have explicit written permission to test. In the UK, unauthorised access to computer systems is a criminal offence under the **Computer Misuse Act 1990** — this project stays entirely legal by staying entirely local.
- Keep the lab on a local/host-only network throughout — no bridging it onto your home network where other devices could be affected.
- Tear down the VM/containers when you're done; don't leave a deliberately vulnerable app running longer than the project needs.

**The single best insight to end on:** most real-world breaches don't need a novel exploit — they exploit the same handful of well-known, well-documented mistakes (the OWASP Top 10) that have been on that list for years. Understanding why those mistakes keep happening — not just how to trigger them — is the mature takeaway.

## The week at a glance

1. **Research & set up** — install Docker, deploy Juice Shop and/or DVWA locally, confirm it is *not* reachable from outside your machine, read up on the OWASP Top 10.
2. **Recon** — run Nmap against your own lab VM to see what's exposed, just like you would (with permission) against a real target.
3. **Find & exploit — first pass** — work through common vulnerability classes (SQL injection, XSS, broken authentication) using OWASP ZAP or Burp Suite Community Edition.
4. **Go deeper** — raise DVWA's difficulty, or try a second app/VM, and compare what does and doesn't work.
5. **Document as you go** — screenshot each successful exploit and record the exact request/payload that triggered it.
6. **Write the fix** — for every vulnerability found, write the real-world remediation.
7. **Compile the report & reflect** — findings table, severity chart, final write-up, teardown.
