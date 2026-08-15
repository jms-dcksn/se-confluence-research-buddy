---
title: Research Scope
kind: research-scope
core: []
adjacent: []
excluded: []
frontier_searches: 5
sweep_activity_days: 14
sweep_max_spaces: 25
max_signals_per_run: 10
synthesis_day: Sunday
destination: TO_BE_CONFIGURED
timezone: TO_BE_CONFIGURED
digest_time: TO_BE_CONFIGURED
last_configured: YYYY-MM-DD
---

# Research Scope

Setup replaces every placeholder above with the confirmed values used by the
wiki and scheduled digest.

## Bands

| Band | Meaning | Who edits it |
| --- | --- | --- |
| `core` | Always searched, every run. The standing watchlist. | You. The digest may propose additions through the inbox but never writes this band. |
| `adjacent` | Searched when it surfaces. Things that keep appearing next to `core` work. | The digest, automatically. It adds entries it keeps encountering and demotes ones that have gone quiet. Every change is logged. |
| `excluded` | Never searched, never recorded as a signal. Noise control. | You only. The digest must never add or remove an entry here. |

`frontier` is not a list. It is the budget below, spent on undirected search
across the whole instance so the wiki can find work that no band names yet.

## Budget

| Field | Meaning |
| --- | --- |
| `frontier_searches` | Undirected searches per run, after the `core` and `adjacent` passes finish. |
| `sweep_activity_days` | Window used to rank spaces by recent update volume. |
| `sweep_max_spaces` | Cap on how many spaces one sweep may sample. Raise it for a small instance, lower it for a noisy one. |
| `max_signals_per_run` | Cap on new signals written per run, so one busy week cannot flood the wiki. |
| `synthesis_day` | Weekday the digest also runs the synthesis pass, which looks for trends across accumulated signals instead of searching Confluence. |

## Discovery log

The digest appends every automatic `adjacent` change here, newest first, with
the date and the evidence that triggered it.
