# Project: Build Your Own 2FA (TOTP) Generator

Every time you type a 6-digit code from Google Authenticator or Authy, there's a well-documented algorithm running underneath it — RFC 6238's Time-based One-Time Password (TOTP) spec, itself built on HMAC-based OTP (RFC 4226). This project implements that algorithm from first principles, rather than importing a library that does it for you.

## What this is (framing for the write-up)

A from-scratch implementation of the same cryptographic algorithm behind real-world two-factor authentication. The point isn't to reinvent something production-ready — it's to understand exactly what "the app generates a new 6-digit code every 30 seconds" actually means at the byte level, and to be able to explain why it's secure.

## Approach by difficulty

### Approachable

- **Core TOTP algorithm** — implement HMAC-SHA1 over a shared secret and the current 30-second time step, truncate to 6 digits, and verify your output matches a real authenticator app given the same secret (most apps let you enter a secret manually instead of scanning a QR code).
- **CLI tool** — wrap it in a command-line tool: `totp generate <secret>` prints the current code, refreshing every 30 seconds like the real thing.

### More ambitious

- **QR code pairing** — generate a `otpauth://` URI and render it as a QR code, so you can scan it with a real phone authenticator app and confirm your implementation and theirs produce identical codes.
- **Full login demo** — build a tiny login flow (even just a local script) that issues a shared secret at "signup," then requires a valid TOTP code at "login" — a working, minimal 2FA system end to end.
- **Time-drift & replay handling** — implement the standard tolerance window (checking the previous/next time step too, for clock drift) and basic replay protection (reject a code that's already been used).

## The analysis

This project's "analysis" is really a security explainer, not a dataset — write up:

- Why is the secret shared once (at setup) but the code never transmitted in a reusable form?
- Why does the time step (not a counter) make TOTP resistant to replay in normal use, and what's the tolerance window for, and what tradeoff does widening it introduce?
- What happens if the shared secret leaks — what's actually protected, and what isn't?
- How does this compare to SMS-based 2FA, and why is TOTP considered stronger?

A short table comparing your generated codes against a real authenticator app's output (same secret, same time) is good concrete evidence the implementation is correct.

## Safety notes that also read as maturity

- Never implement your own primitives for the underlying hash (use a standard library's HMAC/SHA1, don't write your own) — "don't roll your own crypto" applies to the primitives even when the point of the project is implementing the protocol around them.
- Keep any real secrets (e.g. a code you generate for your own actual accounts) out of any repository, screenshots, or write-up — use a throwaway/demo secret for everything you show.
- If you build a login demo, make clear in the write-up that it's a learning project, not something to protect anything real — no genuine account should ever depend on it.

**The single best insight to end on:** TOTP's security doesn't come from the 6-digit code being hard to guess in isolation (it's not, a 6-digit code is only 1 in a million) — it comes from the 30-second window and rate-limited attempts making guessing infeasible in practice. Understanding *why* a mechanism is secure, not just that it is, is the mature takeaway.

## The week at a glance

1. **Research** — read RFC 4226 (HOTP) and RFC 6238 (TOTP), understand HMAC, and how a real authenticator app derives its code.
2. **Implement HOTP** — HMAC over a counter, dynamic truncation to 6 digits; test against known RFC test vectors.
3. **Extend to TOTP** — swap the counter for the current time step; verify your output against a real authenticator app using a shared secret.
4. **Build the CLI** — a tool that displays the current code and counts down to the next refresh.
5. **Add QR pairing** — generate an `otpauth://` URI and QR code for easy setup in a real app.
6. **(Optional) build the login demo** — a minimal end-to-end 2FA flow.
7. **Write up & reflect** — explain why it's secure, compare to SMS-based 2FA, final commit.
