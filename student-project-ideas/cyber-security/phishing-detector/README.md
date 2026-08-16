# Project: Phishing Email Detector

Most real breaches start the same way: someone clicks a link in an email. This project builds a tool that spots the tells a phishing email gives away — using real (but safely archived, non-malicious) samples rather than anything live.

## What this is (framing for the write-up)

A classifier — rule-based or ML — that looks at an email and scores how likely it is to be phishing, based on the same signals a trained human (or a mail provider's spam filter) would look for: mismatched sender domains, urgency language, suspicious links, spoofed headers. It's a data-analysis-meets-security project: the interesting part is *which* signals turn out to matter most.

## Approaches by difficulty

### Approachable

- **Rule-based detector** — a Python script that scores an email on: sender domain vs claimed organisation, urgency/threat language ("act now", "your account will be suspended"), mismatched link text vs actual URL destination, and typosquatted domains (`paypa1.com`, `arnazon.com`, etc.).
- **Header analysis tool** — parse raw email headers (`From`, `Return-Path`, the `Received` chain, SPF/DKIM/DMARC results) to spot spoofing that isn't visible in the email body at all.

### More ambitious

- **ML classifier** — train a simple model (Naive Bayes or logistic regression via scikit-learn) on a labelled phishing/legitimate dataset, and evaluate which features actually drive the prediction.
- **A small web tool or browser extension** — wraps the detector so you paste in an email and get a live score with each flagged reason, which demos far better than a CLI output.

## The analysis

- Which words/features correlate most strongly with phishing (urgency language, generic greetings, mismatched links)?
- If you build a classifier: what's its accuracy, and what does the confusion matrix look like — what kinds of phishing does it miss, and what legitimate mail does it wrongly flag?
- Which domains/TLDs show up most often in your phishing samples?
- Turn your findings into a **phishing red-flags cheat sheet** written from the patterns you actually found — a genuinely useful, standalone output from the project.

Visualise it: a feature-importance chart, a breakdown of tactics used (urgency, spoofed domain, fake attachment, credential harvesting link), an accuracy/confusion-matrix chart if you go the ML route.

## Safety notes that also read as maturity

- Use only **publicly available, pre-collected research datasets** for phishing samples (e.g. established phishing/ham corpora used in academic spam-filtering research) — never send real phishing emails to anyone, and never scrape a live inbox without the owner's explicit consent.
- Keep the whole project passive and read-only: you are analysing archived samples, not interacting with live phishing infrastructure.
- If a sample contains a link, don't click it, even out of curiosity — treat every link in a phishing dataset exactly as if it were live, even in an old archived sample.
- If you do test against your own real inbox with permission, never click a link in a genuine sample — flag/label it, don't visit it.

**The single best insight to end on:** phishing works not because attackers are clever coders, but because they're good at exploiting urgency and trust in a few seconds of a distracted read — the technical tells (a spoofed domain, a mismatched link) are usually there all along if you slow down enough to look. That's a mature, transferable observation about why security awareness training exists.

## The week at a glance

1. **Research & get data** — read about how phishing works and what a mail filter checks for; find a labelled phishing/legitimate email dataset.
2. **Build the rule-based first pass** — score emails on sender/domain mismatch, urgency language, link mismatches; test on obvious examples.
3. **Parse headers** — add SPF/DKIM/DMARC and `Received`-chain checks for spoofing signs the body alone won't show.
4. **(Optional) go ML** — train/test split, pick features, train a simple classifier.
5. **Evaluate** — accuracy, false positives/negatives, and *why* specific examples got missed or misflagged.
6. **Visualise** — feature-importance chart, most common tactics found across your dataset.
7. **Write up & reflect** — your phishing red-flags cheat sheet, final commit.
