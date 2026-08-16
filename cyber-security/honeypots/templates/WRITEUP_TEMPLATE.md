# Honeypot Project Write-Up

**Student name:**
**Date range:**
**Honeypot variant:** (Cowrie / Dionaea / self-written script / web honeypot / honeytokens)
**Host:** (Raspberry Pi on home network / cloud VM / other — do not include public IP or hostname in a shared write-up)

---

## 1. What I built and why

Briefly describe the honeypot: what it emulates, what it's supposed to look like to an attacker, and why you chose this variant over the others.

>

## 2. Threat model & containment

What's the worst case if this honeypot were compromised in a way you didn't anticipate? What did you do to make sure a compromise can't reach anything real?

- **Isolation:** (VM / network segment / firewall rules)
- **What's exposed:** (which port(s), which service(s))
- **What's *not* on this host:** (confirm nothing of real value lives here)
- **Access control:** (how you kept your own admin access — e.g. moved SSH to a non-standard port)

>

## 3. Setup summary

A short, factual account of getting it running — not a full log (that's in your [daily log](DAILY_LOG_TEMPLATE.md)), just enough for a reader to understand what was deployed.

>

## 4. Time to first attack

| Metric | Value |
|---|---|
| Honeypot went live (UTC) | |
| First attack observed (UTC) | |
| Time to first attack | |

A sentence or two on what that gap (or lack of one) tells you.

>

## 5. Findings

### Top source IPs / countries

*(insert chart or table)*

### Top usernames & passwords attempted

*(insert chart or table)*

### Commands run / malware fetched after "login"

>

### Anything unexpected

Attacks or patterns that surprised you — a specific technique, an unusual payload, a burst of activity, a tool you didn't expect.

>

## 6. Analysis script(s)

Link to or briefly describe the script(s) you wrote to parse the logs. What did they extract, and what would you improve if you kept working on this?

>

## 7. Reflection

The main write-up frames the single best insight as: *most attacks aren't targeted geniuses — they're relentless automated bots trying the same weak passwords millions of times.* Does your data support that? What's your own version of that takeaway, in your own words?

>

## 8. Safety & teardown confirmation

- [ ] Host isolated from anything containing real data throughout the project
- [ ] Any captured malware/samples never executed outside the sandbox
- [ ] Cloud VM (if used) torn down after data collection
- [ ] No credentials, keys, or sensitive data were ever placed on the honeypot host
- [ ] This project ran only on infrastructure I own or am authorised to use

**Teardown date / confirmation:**
>
