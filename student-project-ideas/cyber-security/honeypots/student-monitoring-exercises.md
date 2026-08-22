# Watching a Live Server — A Three-Day Introduction

This machine is a real server on the public internet. Right now, while you read this, strangers are trying to log into it. They will fail, but they leave traces, and you can read them.

Over the next few days you'll learn to answer three questions about any Linux machine:

1. **Who has logged in?**
2. **Who has tried and failed?**
3. **What is running, and who is it talking to?**

These are the first questions a system administrator asks, and they're the same on almost any Linux system you'll ever touch.

---

## Ground rules

**Everything here is read-only.** Not one command in this guide changes anything. You can't break the machine by running them, so run them freely, including the ones you don't fully understand yet.

**You don't have admin rights, and that's deliberate.** Some things won't work. That's the design, not a bug. If you hit "Permission denied" on something in this guide, tell the admin — it might mean a setup step got missed.

**If you find something odd, don't fix it. Report it.** More on this at the end. It's the single most important habit in this guide.

**Ask questions.** Output you don't understand is the interesting part. Nobody reads `ss -tulpn` output correctly the first time.

---

## Before you start

Check you have the right permissions:

```bash
id
```

You should see `adm` and `systemd-journal` in the groups list. `adm` lets you read the log files, `systemd-journal` lets you read the system journal. Without them most of this guide returns nothing useful. If they're missing, log out and back in first — group changes only take effect at login. Still missing after that, tell the admin.

Make somewhere to keep notes:

```bash
mkdir -p ~/notes
```

You'll use it each day. Keeping a record is not busywork — the whole skill here is noticing *change*, and you can't notice change without a record of before.

---

# Day 1 — Who has logged in

## The command to start with

```bash
last
```

This reads a binary file the system maintains of every login. Output looks like:

```
vajirag  pts/0   86.12.44.9    Fri Aug 22 09:14   still logged in
nethu    pts/1   86.12.44.9    Thu Aug 21 16:02 - 17:31  (01:29)
reboot   system boot 6.1.0-18  Thu Aug 21 08:00   still running
```

Left to right: **who** logged in, **which terminal** they got, **where they connected from**, **when** it started, and **how long** it lasted.

`pts/0` means a pseudo-terminal — a remote session over SSH. Numbers increment as sessions open, so `pts/3` just means it was the fourth session open at that moment. Nothing significant about the number itself.

Try these variations:

```bash
last -20          # just the last 20 entries
last -F           # full timestamps, including the year
last nethu        # only your own logins
last reboot       # only restarts
```

`last reboot` is worth knowing. An unexplained restart on a server is always worth asking about.

## Who is on the machine right now

```bash
w
```

```
 09:22:14 up 1 day,  1:22,  2 users,  load average: 0.02, 0.05, 0.01
USER     TTY      FROM         LOGIN@   IDLE   WHAT
vajirag  pts/0    86.12.44.9   09:14    0.00s  w
nethu    pts/1    86.12.44.9   09:20    2:31   -bash
```

The top line is a system summary; the table is current sessions. `IDLE` is how long since that person last typed anything, and `WHAT` is the command they're running right now.

Try `who -a` for a similar view in a different format, and `lastlog` for the most recent login of *every* account — including accounts that have never logged in at all, which is useful information in itself.

## Reading the log file directly

`last` reads a compact binary file. The text log has far more detail:

```bash
grep 'Accepted publickey' /var/log/auth.log
```

Every line is one successful login. You'll see something like:

```
Aug 22 09:14:02 project-vm sshd[8842]: Accepted publickey for vajirag from 86.12.44.9 port 51234 ssh2: ED25519 SHA256:aBc...
```

There's a lot in that line: the timestamp, the machine name, the process and its PID, the account, the source IP, and the fingerprint of the key that was used. That fingerprint is how you'd tell *which* of someone's keys authenticated — useful when a person has several.

"publickey" is the authentication method. On this machine it's the only one allowed — passwords are switched off entirely, which is why you'll never see a password login here.

## The counting pattern

Here's an idiom you'll use constantly in Linux. Learn it properly, because it generalises to almost anything:

```bash
grep 'Accepted publickey' /var/log/auth.log \
  | grep -oE 'from [0-9.]+' \
  | sort | uniq -c | sort -rn
```

Read it right to left as a pipeline, where each `|` passes output to the next command:

1. `grep 'Accepted publickey'` — keep only successful-login lines
2. `grep -oE 'from [0-9.]+'` — from each line, print *only* the matching part (`-o`) using a regular expression (`-E`), so you get `from 86.12.44.9`
3. `sort` — group identical lines together
4. `uniq -c` — collapse duplicates and prefix each with a count
5. `sort -rn` — sort by that count, reverse (`-r`), numerically (`-n`)

Result: a list of source IPs with how many times each logged in, most frequent first.

`sort | uniq -c | sort -rn` is the pattern. Anything you can get one-per-line, you can count this way. Try it on accounts instead:

```bash
grep 'Accepted publickey' /var/log/auth.log | awk '{print $9}' | sort | uniq -c | sort -rn
```

`awk '{print $9}'` prints the ninth whitespace-separated field of each line — the username. Count the fields in a real line to see why it's 9.

## Older logs

Logs rotate: `auth.log` is current, `auth.log.1` is the previous period, and older ones are gzipped as `auth.log.2.gz` and so on.

```bash
ls -la /var/log/auth.log*
zgrep 'Accepted publickey' /var/log/auth.log.*.gz 2>/dev/null
```

`zgrep` is `grep` that reads compressed files without unpacking them. There's `zcat` and `zless` too.

## Day 1 exercise

Save a record:

```bash
{ echo "=== $(date) ==="; last -30; echo; grep 'Accepted publickey' /var/log/auth.log | tail -20; } > ~/notes/day1-logins.txt
```

Then, in your own words, write down:

- How many separate accounts have ever logged into this machine?
- How many distinct IP addresses appear in the successful logins?
- What's the earliest login still in the logs?
- Is there any login you *can't* account for?

That last question is the one that matters. On a machine this size, every successful login should have an explanation.

---

# Day 2 — Who is trying to get in

Yesterday was legitimate access. Today is everyone else.

## Look at the volume

```bash
grep -c 'Invalid user' /var/log/auth.log
```

`-c` counts matching lines instead of printing them. The number will probably surprise you — hundreds or thousands is normal for a server that's been up a few days.

Now look at what they actually are:

```bash
grep 'Invalid user' /var/log/auth.log | tail -30
```

These are automated scanners working through lists of common usernames. They aren't targeting you or this project. Every machine with a public IP gets this traffic continuously, starting within minutes of coming online.

## Where from

```bash
grep 'Invalid user' /var/log/auth.log \
  | grep -oE '[0-9]{1,3}(\.[0-9]{1,3}){3}' \
  | sort | uniq -c | sort -rn | head -20
```

Same counting pattern as yesterday. The regex `[0-9]{1,3}(\.[0-9]{1,3}){3}` means "one to three digits, then that pattern preceded by a dot, three more times" — an IPv4 address.

## What names they're guessing

```bash
grep 'Invalid user' /var/log/auth.log \
  | awk '{print $8}' | sort | uniq -c | sort -rn | head -20
```

You'll see `admin`, `root`, `test`, `ubuntu`, `oracle`, `postgres`, `git`, `user`, `pi`. These are defaults — accounts that exist on badly configured machines. The scanners try them because on a small percentage of servers, they work with a default password.

**Notice what's absent: your username.** They can't guess it, and even if they did, there's no password to try. Two separate reasons the attack fails.

## What the different messages mean

Because passwords are disabled here, you'll never see `Failed password`. Instead:

| What you see | What happened | Should you care? |
|---|---|---|
| `Invalid user bob from 1.2.3.4` | Guessed a username that doesn't exist | No — constant background noise |
| `Connection closed by authenticating user nethu` | Real username, wrong key | **Yes, mention it** |
| `maximum authentication attempts exceeded` | Client tried several keys | Mild |
| `error: kex_exchange_identification` | Scanner or broken client | No |
| `Accepted publickey for X` | **Someone got in** | Check you know who |

Row two is the interesting one. It means someone used a *real* username on this machine. Since your usernames aren't guessable defaults, that implies they learned it somewhere — which is worth mentioning even though the login still failed.

Look for it:

```bash
grep 'Connection closed by authenticating' /var/log/auth.log
```

Quite possibly empty. Empty is a good result.

## The journal

Same information, different tool:

```bash
journalctl -u ssh --since today
journalctl -u ssh --since "1 hour ago"
journalctl -u ssh -n 50
```

`-u ssh` filters to the SSH service, `-n 50` shows the last 50 lines. The journal is systemd's structured log — it holds output from every service, not just what's written to files in `/var/log`.

Now watch it live:

```bash
journalctl -u ssh -f
```

`-f` follows, printing new lines as they arrive. Leave this running in a terminal for a few minutes. On a public IP you will very likely see connection attempts appear in real time.

`Ctrl-C` to stop.

## Day 2 exercise

Take a count and keep it:

```bash
{ echo "=== $(date) ==="; echo "Invalid user total: $(grep -c 'Invalid user' /var/log/auth.log)"; echo; echo "Top source IPs:"; grep 'Invalid user' /var/log/auth.log | grep -oE '[0-9]{1,3}(\.[0-9]{1,3}){3}' | sort | uniq -c | sort -rn | head -10; echo; echo "Top usernames tried:"; grep 'Invalid user' /var/log/auth.log | awk '{print $8}' | sort | uniq -c | sort -rn | head -10; } > ~/notes/day2-probes.txt
```

Then think about:

- Roughly how many attempts per hour is that?
- Does one IP dominate, or is it spread across many?
- Any usernames in the list that look specific to *this* machine rather than generic defaults?
- Why doesn't this traffic worry the admin much?

**Run the same count again tomorrow.** The rate of change is what matters. Going from 200 a day to 20,000 a day means something changed; a steady 200 a day is just the internet being the internet.

---

# Day 3 — What's running and what it's talking to

## Processes

```bash
ps aux | head -20
```

`ps` lists processes; `aux` is a conventional flag combination meaning roughly "all processes, with user names, including ones with no terminal." The columns: user, PID, %CPU, %MEM, memory figures, terminal, state, start time, CPU time used, and the command.

Sort by resource use:

```bash
ps aux --sort=-%cpu | head -20
ps aux --sort=-%mem | head -20
```

The minus sign means descending. Without it you'd get the quietest processes first.

A tidier view:

```bash
ps -eo user,pid,etime,pcpu,pmem,comm --sort=-pcpu | head -20
```

`-eo` means "all processes, output these columns." `etime` is elapsed time since the process started — helpful for spotting something that began at an odd moment.

Interactively:

```bash
htop
```

`F6` changes the sort column, `F5` toggles a tree view showing which process started which, `q` quits. Spend a few minutes here. The tree view makes the shape of a Linux system much clearer than any static list.

Your own processes only:

```bash
ps -u nethu
pstree -p
```

## Load

```bash
uptime
```

```
 09:22:14 up 1 day,  1:22,  2 users,  load average: 0.02, 0.05, 0.01
```

Three load averages: 1, 5, and 15 minutes. Compare them to the CPU count:

```bash
nproc
```

Roughly: load equal to the core count means fully busy. Well above it, sustained, means something is saturated. Near zero means idle. On a project VM that isn't doing anything, expect near zero — so a high reading with no obvious cause is a real question.

```bash
free -h     # memory
df -h       # disk space
```

`-h` means human-readable — GB and MB instead of raw blocks. Worth remembering; lots of tools accept it.

## The network

This is the most useful command in the guide:

```bash
ss -tulpn
```

The flags: `t` TCP, `u` UDP, `l` listening, `p` show process, `n` numeric ports rather than names.

This lists every port the machine is **listening on** — every door where something outside could knock. On a small project VM the list should be short: SSH on 22, maybe a web server, maybe a database bound to localhost.

Look at the `Local Address:Port` column carefully. `0.0.0.0:22` means listening on all interfaces, reachable from outside. `127.0.0.1:5432` means localhost only — nothing outside the machine can reach it. That distinction is one of the most important ideas in server security, and this column is where you read it.

Process names appear blank for other users' processes. Expected, not a problem.

Current connections:

```bash
ss -tn state established
```

Live TCP connections. Column 4 is this machine's end, column 5 is the other end. Your own SSH session is in there — find it.

Count where connections come from:

```bash
ss -tn state established | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn
```

The counting pattern again. `cut -d: -f1` splits on `:` and keeps field 1, stripping the port off an `IP:port` string.

Your own SSH sessions specifically:

```bash
ss -tn state established '( dport = :22 or sport = :22 )'
```

## What "wrong" would look like

For calibration, the classic signature of a compromised cloud VM is cryptomining, and it looks like:

- Load average pinned at or above the core count, continuously, with no explanation
- A process using ~100% CPU with a random or oddly generic name
- Steady outbound connections to an unfamiliar address, often on port 3333, 4444, 5555, or 14444
- A listening port that nobody installed

Any one alone might be innocent. Together they're a pattern. You almost certainly won't see this — but knowing the shape is the point of looking every day.

## Day 3 exercise

Record a snapshot:

```bash
{ echo "=== $(date) ==="; uptime; echo; nproc; echo; free -h; echo; df -h; echo "--- Listening ports ---"; ss -tulpn; echo "--- Established ---"; ss -tn state established; echo "--- Top CPU ---"; ps aux --sort=-%cpu | head -10; } > ~/notes/day3-system.txt
```

Then:

- How many ports is the machine listening on? What is each one for?
- Which are on `0.0.0.0` (public) and which on `127.0.0.1` (local only)?
- What's the busiest process, and does its name make sense?
- What's the load average, and is that reasonable for what this machine is doing?

Ask the admin about anything on that list you can't explain. "What's this port for?" is a perfectly good question, not an admission of ignorance.

---

# Keeping it up

The value of all this comes from repetition. One snapshot tells you almost nothing; a week of them tells you what's normal, and *then* an anomaly becomes visible.

Run this each day and save it:

```bash
{
  echo "=== $(date) ==="
  echo "-- Recent logins --";        last -10
  echo "-- Successful SSH --";       grep -c 'Accepted publickey' /var/log/auth.log
  echo "-- Probe attempts --";       grep -c 'Invalid user' /var/log/auth.log
  echo "-- Load --";                 uptime
  echo "-- Listening ports --";      ss -tulpn
} >> ~/notes/daily.txt
```

Note the `>>` — two arrows append, one arrow overwrites. Getting that wrong wipes your history, and it's a mistake most people make exactly once.

After a few days:

```bash
cat ~/notes/daily.txt
grep 'Probe attempts' -A1 ~/notes/daily.txt
```

Watch how the numbers move. That trend line is the actual skill.

---

# Cheat sheet

**Logins**
```bash
last -20                                         # recent logins
w                                                # who's on now
lastlog                                          # last login per account
grep 'Accepted publickey' /var/log/auth.log      # successful SSH
```

**Probing**
```bash
grep -c 'Invalid user' /var/log/auth.log         # count attempts
grep 'Invalid user' /var/log/auth.log | tail -20
journalctl -u ssh -f                             # live SSH log
```

**System**
```bash
uptime && nproc                                  # load vs cores
free -h                                          # memory
df -h                                            # disk
htop                                             # interactive
ps aux --sort=-%cpu | head                       # busiest
```

**Network**
```bash
ss -tulpn                                        # listening ports
ss -tn state established                         # live connections
```

**The counting pattern**
```bash
<something producing lines> | sort | uniq -c | sort -rn | head
```

**Useful flags:** `-h` human-readable · `-c` count · `-n` numeric · `-r` reverse · `-f` follow · `2>/dev/null` hide permission errors

---

# If something looks wrong

**Tell the admin. Don't fix it, don't delete it, don't investigate further.**

This isn't about trust — it's what professional incident responders do, for three concrete reasons:

1. Deleting a suspicious file destroys the evidence needed to work out what else was touched.
2. If someone really is in the machine, unusual activity from your account tells them they've been spotted.
3. The right response needs cloud-level access you don't have — snapshotting the disk, cutting network access, revoking keys.

Specifically: **don't reboot, don't shut down, don't kill processes, don't edit or remove anything.** Shutting down loses everything in memory, which is often where the useful evidence is.

When you report, include the exact command you ran and its exact output — copy and paste rather than describing it — plus when you noticed and anything unusual you'd done beforehand.

**Report a false alarm rather than staying quiet about a real one.** Getting it wrong costs a two-minute conversation. Nobody will mind, and "I saw this and wasn't sure" is exactly the right instinct.

---

# What you've actually learned

The commands are specific to Linux, but the habits transfer everywhere:

- **Read logs before guessing.** The machine usually already recorded what happened.
- **Baseline first, compare later.** "Is this normal?" is unanswerable without a record of normal.
- **Rate of change beats absolute numbers.** 200 probes a day forever is fine. 200 becoming 20,000 is a question.
- **Know what you can't see.** Traffic blocked by the cloud firewall never reaches this machine and appears in none of these logs. A quiet log means nothing got *past* the firewall — not that nobody tried.
- **Escalate early.** Noticing is a full contribution. You don't have to also be the one who fixes it.

The last one is worth taking seriously. In real operations, most incidents are caught by someone junior who thought a number looked wrong and said so.
