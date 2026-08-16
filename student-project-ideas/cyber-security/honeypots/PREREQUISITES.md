# Prerequisites

A pre-project checklist for anyone starting from zero on git, Markdown, networking, or the command line. Work through this **before** Day 1 of the [week at a glance](README.md#the-week-at-a-glance) — none of it is honeypot-specific, but all of it is assumed once the week starts.

If you're already comfortable with git, Markdown, TCP/networking basics, and the terminal, skip straight to the README's [Getting started](README.md#getting-started) section.

---

## 1. Markdown

You'll be editing `README.md`, `DAILY_LOG.md`, and `WRITEUP.md` all week.

- [ ] Learned the basics: headers (`#`), bullet/numbered lists, bold/italic, code blocks (\`\`\`), links `[text](url)`, tables.
- [ ] Practiced: opened [templates/DAILY_LOG_TEMPLATE.md](templates/DAILY_LOG_TEMPLATE.md) in a text editor and a Markdown previewer (VS Code has one built in — `Cmd+Shift+V`) side by side, and typed a heading and a bullet list to see them render.

**Ready when:** you can write a heading, a list, and a fenced code block, and confirm they render correctly in a preview.

---

## 2. Git & GitHub

Needed for the "Set up GitHub" and "Create your project repository" steps.

- [ ] Understand the concepts, not just commands: a **repository** is a folder git tracks; a **commit** is a saved snapshot with a message; **push** sends commits to GitHub; **clone** downloads a repo to your machine.
- [ ] Installed git, created a GitHub account, ran the one-time `git config` identity commands (see README's [Set up GitHub](README.md#1-set-up-github)).
- [ ] Practiced on a throwaway repo before touching the real one: create a test repo, clone it, make a file, `git add` → `git commit` → `git push`. Repeat 2–3 times until it feels boring.
- [ ] Understand `.gitignore` and secrets hygiene: never commit VM passwords, API keys, or SSH private keys. If you're not sure whether something is sensitive, leave it out and ask first.

**Ready when:** you can create a file, commit it with a message, and see it appear on GitHub.com without looking up each command.

---

## 3. TCP / networking basics

This is the *why* behind the whole project — skip it and the honeypot is just "run this script."

- [ ] Understand what an **IP address** and a **port** are, what it means for a service to **listen** on a port, client vs. server, and what **SSH** (port 22) normally does.
- [ ] Understand why bots specifically target port 22/23 (SSH/Telnet) — it's the internet's most-scanned port, which is exactly why Cowrie fakes it.
- [ ] If deploying at home: understand **port forwarding** at a basic level (your router maps an external port to a device on your internal network) — you'll need this to expose the honeypot.

**Ready when:** you can explain in one sentence what happens when a bot "connects to port 22," and why moving your real SSH off port 22 protects you.

---

## 4. Command line & remote access

Needed once you SSH into the honeypot host (Day 2 onward) — there's no desktop there, so navigation, editing, and log reading happen entirely in the terminal.

**Basic shell navigation**
- [ ] Comfortable with `cd`, `ls`, `mkdir`, `chmod`, and `sudo` — you'll use all of these while provisioning the host.

**SSH itself**
- [ ] Know how to connect: `ssh user@host` and `ssh -p <port> user@host` once you move to a non-standard port.
- [ ] Ideally set up key-based auth instead of a password: `ssh-keygen` to generate a key pair, `ssh-copy-id` to install your public key on the host.
- [ ] **Before** changing your host's SSH port, confirm you have a fallback way in — a cloud provider's web-based console (DigitalOcean/AWS both have one), or physical/keyboard access for a Raspberry Pi. This is the single most common way people accidentally lock themselves out.

**Keeping things running after you disconnect**
- [ ] Know how to use `tmux` or `screen` (or `nohup`/a `systemd` service) so the honeypot keeps running after you close the SSH session — otherwise it dies the moment you disconnect.

**vim** (or nano as an easier fallback)
- [ ] Know the survival set: `i` to enter insert mode and type, `Esc` to leave insert mode, `:wq` to save and quit, `:q!` to quit without saving.
- [ ] Ran `vimtutor` (ships with vim, ~20–30 min interactive tutorial) — or, if vim feels like too much right now, used **nano** instead (`Ctrl+O` save, `Ctrl+X` exit). You can always come back to vim later.

**less**
- [ ] Know the core commands: `less filename` to open, `Space`/`b` to page down/up, `/searchterm` then `Enter` to search, `n` for next match, `q` to quit.
- [ ] Practiced on an existing text file, including searching for a string in it.

**Ready when:** you can SSH into a remote machine (or a local VM as practice), edit a file, start a long-running process inside `tmux`/`screen`, detach, and reconnect — and separately, open a log file in `less` and search it.

---

## 5. Decide your deployment target

The README's safety section assumes you've already chosen this — decide before Day 2 ("Provision & harden the host"):

- [ ] **Raspberry Pi at home** — cheaper, more hands-on, less attack traffic, requires router access for port forwarding.
- [ ] **Cloud VM** (DigitalOcean/AWS, cheap tier) — more attack traffic, no router config needed, but check provider terms and remember to tear it down after.

**Ready when:** you've picked one and (if cloud) created the account, or (if Pi) confirmed you have router admin access.

---

## 6. Environment check

- [ ] Python 3 installed (`python3 --version`) — needed for [example-simple-honeypot/](example-simple-honeypot/) and the analysis scripts.
- [ ] Know how to create and use a Python virtual environment (`python3 -m venv venv`, then activate it) before running `pip install -r requirements.txt` — keeps project dependencies isolated from your system Python.
- [ ] Picked a text editor you're comfortable in (VS Code is a safe default — free, with a built-in Markdown preview and terminal).

---

## 7. For the analysis phase (Days 5–6)

You won't need this until later in the week, but it's worth knowing it's coming.

- [ ] **JSON basics** — Cowrie logs in JSON (`cowrie.json`); you'll need to read/parse JSON to extract IPs, usernames, and commands.
- [ ] **A charting approach** — e.g., `pandas`/`matplotlib` in Python — for the top-passwords chart, GeoIP map, and attack timeline the README asks for.
- [ ] **UTC vs. local time** — the daily log template asks for timestamps in UTC specifically; know how to get UTC time on the host (`date -u`) so your timeline is consistent regardless of where you and the server are.

**Ready when:** you can load a small JSON file in Python and print one field from it, and you know which charting library you'll reach for.

---

Once everything above is checked off, start at [Getting started → 1. Set up GitHub](README.md#1-set-up-github) and follow the [week at a glance](README.md#the-week-at-a-glance).
