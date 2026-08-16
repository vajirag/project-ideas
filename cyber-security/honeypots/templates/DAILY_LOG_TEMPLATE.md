# Daily Research Log

A running journal for the week. Fill in one section per day (or per session) as you go — this is your raw material for the final [write-up](WRITEUP_TEMPLATE.md), so capture things while they're fresh rather than trying to reconstruct them later.

**Student name:**
**Project variant** (Cowrie / Dionaea / self-written script / web honeypot / honeytokens):
**Host** (Raspberry Pi / cloud VM / other):
**Week starting:**

---

## Day 1 — Research & threat model

- [ ] Read about how the chosen honeypot works
- [ ] Wrote down what could go wrong if this is misconfigured
- [ ] Decided on containment (isolated VM / network segment / firewall rules)

**Notes:**
>

**What could go wrong, and how I'm containing it:**
>

---

## Day 2 — Provision & harden the host

- [ ] Host provisioned (OS, provider/hardware, region if cloud)
- [ ] Own SSH access moved to a non-standard port
- [ ] Confirmed I can still log in on the new port *before* touching port 22/2222
- [ ] Router/firewall rule pointing external port 22 → honeypot port (if applicable)

**Notes / gotchas:**
>

**Command(s) used to move SSH and verify access:**
```

```

---

## Day 3 — Install & configure

- [ ] Honeypot installed and running
- [ ] Tested it myself from another machine (does it look convincing?)
- [ ] Logging confirmed working (a self-triggered event shows up in the log)

**Notes:**
>

---

## Day 4 — Go live & collect

**Time honeypot went live (UTC):**
**Time of first observed attack (UTC):**
**Time-to-first-attack:**

**Notes on what the first few hours looked like:**
>

---

## Day 5 — Parse the logs

- [ ] Wrote/ran a script to extract IPs, usernames, passwords, commands
- [ ] Spot-checked a handful of raw log entries by hand to sanity-check the parser

**Anything the parser missed or got wrong initially:**
>

---

## Day 6 — Analyse & visualise

- [ ] Top-passwords chart
- [ ] GeoIP map / top-countries chart
- [ ] Attack timeline

**Interesting or surprising numbers so far:**
>

---

## Day 7 — Findings, reflection & teardown

- [ ] Final write-up drafted (see [WRITEUP_TEMPLATE.md](WRITEUP_TEMPLATE.md))
- [ ] VM/host torn down (if cloud)
- [ ] Confirmed no captured malware or credentials left lying around outside the sandbox
- [ ] Final commit made

**Teardown confirmation (what was deleted, when):**
>

**One thing I'd do differently next time:**
>
