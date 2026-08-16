# Project: Honeypots

Honeypots are purely defensive, produce real data from actual attackers hitting your decoy, and the analysis writes itself into a great project with exposure to lots of areas to learn.

## What a honeypot is (framing for the write-up)

A decoy system designed to look attractive and vulnerable, so you can observe attackers without risking anything real. Nothing of value lives on it. Its whole job is to be attacked and logged.

That "I built a trap and studied what got caught" narrative is genuinely compelling as a project, and you can expand this to create different variants and continue the project forward.

## Honeypots by difficulty

### Approachable

- **Cowrie** — the classic. A fake SSH/Telnet server that lets bots "log in," records every command they type, and even captures malware they try to download. Within hours of exposure you'll see automated attacks. Superb data.
- **Dionaea** — emulates vulnerable services (SMB, FTP, etc.) to capture malware samples.
- **A simple port honeypot you write yourself** — a small Python script that listens on a port, logs every connection and what's sent. Writing it yourself shows real coding skill and total understanding of what it does.

### More ambitious

- **HTTP/web honeypot** — mimic a vulnerable web app or admin login and log the exploit attempts and credential-stuffing you catch.
- **Honeytokens** — fake credentials or files that alert you the moment anyone touches them. Clever and low-effort; shows lateral thinking.

## The analysis

The honeypot is only half the project — the value is what you do with the logs:

- Where are attacks coming from (map source IPs to countries)?
- What usernames and passwords do bots try most? (You'll see root/root, admin/123456 endlessly — great for a chart.)
- What commands do they run after "logging in"? What malware do they fetch?
- How fast does a fresh server get attacked? Timing the first hit is a striking stat.
- Turn it into visualisations — a bar chart of top passwords, a timeline of attacks — which is exactly the kind of evidence that stands out.

## Safety notes that also read as maturity

- Run it in an isolated VM/network segment so a compromise can't reach anything real — this is the whole discipline of honeypot deployment, and saying so shows you understand it. You can configure a Raspberry Pi, and open a port within your home router.
- A cloud VM (a cheap DigitalOcean/AWS instance) gets far more interesting internet-wide attack traffic than a home network — but tear it down afterward and never store anything sensitive on it. Check the provider's terms.
- Only ever run a honeypot on infrastructure you own or are authorised to use.
- Handle any captured malware carefully — keep it in the VM, never execute it outside the sandbox.

**The single best insight to end on:** a honeypot teaches you that most attacks aren't targeted geniuses — they're relentless automated bots trying the same weak passwords millions of times. Understanding that shapes how you think about defence, and it's a mature observation for a personal statement.

## The week at a glance

1. **Research & threat model** — understand honeypots, write down what could go wrong and how you'll contain it.
2. **Provision & harden the host** — the key challenge: move your own SSH to a non-standard port so you keep admin access while port 22 goes to the attackers.
   - If you are running this on a Raspberry Pi, Cowrie listens on 2222 by default; point your router's external port 22 to 2222.
3. **Install & configure Cowrie** — make a convincing fake SSH server and test it yourself.
4. **Go live & collect** — open port 22 and record how long until the first attack (often minutes).
5. **Parse the logs** — write a small script to extract IPs, usernames, passwords, commands.
6. **Analyse & visualise** — top-password chart, GeoIP map, attack timeline.
7. **Findings & reflection** — write it up, tear the VM down, final commit.

## Getting started

New to git, Markdown, TCP/networking, or the command line? Work through **[PREREQUISITES.md](PREREQUISITES.md)** first — it's a checklist covering exactly what this project assumes you already know.

### 1. Set up GitHub

If you don't already have one:

1. Create a free account at [github.com/signup](https://github.com/signup).
2. Install Git locally if it's not already there — check with `git --version`; if missing, see [git-scm.com/downloads](https://git-scm.com/downloads).
3. Set your identity (one-time, used on every commit you make):
   ```bash
   git config --global user.name "Your Name"
   git config --global user.email "you@example.com"
   ```

### 2. Create your project repository

1. On GitHub, click **New repository** — name it something like `my-honeypot-project`, keep it private if you'd rather not publish attack data publicly, and initialize it with a README.
2. Clone it locally:
   ```bash
   git clone https://github.com/<your-username>/my-honeypot-project.git
   cd my-honeypot-project
   ```
3. Create the basic project structure:
   ```bash
   mkdir -p logs analysis
   touch README.md
   ```
   `logs/` will hold your captured data, `analysis/` your parsing/charting scripts.
4. Copy the templates in (see below), then make your first commit:
   ```bash
   git add .
   git commit -m "Initial project setup"
   git push
   ```

Commit regularly as you go through the week (after setup, after going live, after each analysis step) — a commit history that shows the project evolving is itself part of the evidence of your work.

**Before your first real commit of captured data:** double-check `.gitignore` excludes anything you wouldn't want public (raw logs with real attacker IPs are usually fine to share, but check your host's terms; never commit captured malware samples).

### 3. Use the example and templates

- **[example-simple-honeypot/](example-simple-honeypot/)** — a working example of the self-written port honeypot option, with logging and log-analysis scripts already wired up.
- **[templates/](templates/)** — a daily log and a final write-up template. Copy both into your own project folder rather than editing them in place, so the templates stay clean for the next person:
  ```bash
  cp templates/DAILY_LOG_TEMPLATE.md my-project/DAILY_LOG.md
  cp templates/WRITEUP_TEMPLATE.md my-project/WRITEUP.md
  ```
