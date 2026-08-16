# Project: Digital Footprint / OSINT Audit

Attackers don't start with a hack — they start with research. This project runs that same research process (open-source intelligence, or OSINT) against yourself, entirely using public, passive tools, to see exactly how much a stranger could learn about you in an afternoon — and then locks it down.

## What this is (framing for the write-up)

A self-directed OSINT investigation: gathering everything publicly discoverable about one person (you, or a friend who's given explicit consent) using only passive, legal techniques — no hacking, no accessing anything private, just piecing together what's already public. It's the recon phase real attackers use for social engineering and targeted phishing, run here for defensive, self-auditing purposes.

## Approach by difficulty

### Approachable

- **Search engine reconnaissance** — Google dorking (`site:`, `filetype:`, `intitle:` operators) to find what's indexed about you: old accounts, forum posts, documents with your name in them.
- **Social media metadata review** — what do your public profiles reveal in combination (school/employer, location patterns from photo backgrounds, friend/follower lists, old posts you forgot were public)?
- **WHOIS / domain lookups** — if you own a domain, what does its WHOIS record expose (unless privacy-protected)?

### More ambitious

- **Certificate transparency logs** — search [crt.sh](https://crt.sh) for TLS certificates issued for any domains/subdomains you control, which can reveal infrastructure you forgot was public (old subdomains, staging environments).
- **Shodan lookup on your own IP** — see what your home network's public IP exposes to internet-wide scanners (pairs well with the [Home Network Security Audit](../home-network-audit/) project).
- **Cross-referencing / correlation** — combine findings across sources: does a username reused across platforms link a "private" account to your real identity? Does EXIF data in a publicly posted photo reveal a location?

## The analysis

- What did you find that surprised you — something you thought was private, or had forgotten was public?
- Which single piece of information, if an attacker had it, would be most useful for a targeted phishing attempt or social engineering pretext against you?
- How much of what you found came from *you* posting it, versus from third parties (tagged photos, data broker sites, old accounts)?
- What's realistically fixable (delete/lock down) versus what's out of your control?

Write it up as a findings report: a table of what was found, where, and its sensitivity level, plus a prioritised "lock this down first" action list — genuinely useful output, not just an exercise.

## Safety notes that also read as maturity

- Only investigate yourself, or someone else **with their explicit, informed consent** given in advance — OSINT on a person without consent, even using only "public" information, can cross into harassment or stalking and should never be done about anyone else without it.
- Stay strictly passive: searching, viewing, and cross-referencing public information is fine; attempting to access anything private (guessing passwords, requesting password resets to see what's revealed, contacting people under a false pretext) is not part of this project and moves into territory requiring separate authorisation.
- Don't publish the actual findings about a real person (even yourself) in a public write-up — write up the *methodology and lessons learned* publicly, and keep the specific personal findings private or redacted.
- If you find something genuinely concerning (e.g. a data breach exposing your real password), treat it seriously — change the password, enable 2FA, and consider it a finding worth acting on immediately rather than just writing up.

**The single best insight to end on:** most of what's discoverable about someone isn't from a single dramatic leak — it's from years of small, individually-harmless posts that only become revealing once someone deliberately correlates them. That's a genuinely useful, mature thing to understand about your own online presence, and it reframes "privacy" as an aggregation problem, not a single-setting problem.

## The week at a glance

1. **Research & consent** — read about OSINT methodology and its legal/ethical boundaries; if investigating anyone but yourself, get explicit consent first.
2. **Search engine recon** — Google dorking and general web search for your name/handles.
3. **Social media & platform review** — audit what's public across every platform you use.
4. **Infrastructure lookups** — WHOIS, certificate transparency, Shodan (if applicable).
5. **Cross-reference & correlate** — look for links between accounts/identities that weren't individually obvious.
6. **Lock it down** — act on what you found: tighten privacy settings, remove what you can, enable 2FA where relevant.
7. **Write up & reflect** — methodology write-up (public-safe), private findings report, final commit.
