# Scheduled digest contract

Before retrieval, read `AGENTS.md`, `wiki/research-scope.md`, `wiki/index.md`,
the current month's log, and the automation memory when it exists. A missing
memory record is valid on the first run; initialize it after completing that
run. Verify that the exact topics, destination, digest time, and timezone
embedded above this contract match `wiki/research-scope.md`; stop and report
the mismatch instead of guessing.

This job has two jobs. The scoped passes keep known work current. The discovery
pass looks for work nobody told you about. Do not let the first crowd out the
second: a run that reports only scoped updates and skips discovery has failed
its second job, and should say so rather than quietly omitting it.

Create at most one `raw/confluence/YYYY-MM-DD-daily-digest.md` per calendar
date. If a completed record already exists, verify it and exit without creating
another. Create a new digest from `templates/digest.md` and replace every
placeholder.

## Pass 1 — core

Search every entry in `core` through Atlassian Rovo. Prioritize sources updated
within seven days. Record material changes and explicit no-change coverage for
every core entry, so silence is visible as a checked result rather than an
omission.

## Pass 2 — adjacent

Search every entry in `adjacent` the same way, but do not require no-change
coverage for it. Adjacent entries are being watched on suspicion, not on
commitment.

After searching, maintain the band:

- Promote to `adjacent` anything that surfaced in two or more separate runs
  while searching `core`, and is not already in `core`, `adjacent`, or
  `excluded`.
- Demote from `adjacent` anything with no material result across the last five
  runs.
- Append every promotion and demotion to the discovery log in
  `wiki/research-scope.md`, with the date and the evidence that triggered it.

You may edit the `adjacent` band directly. You must never edit `core` or
`excluded` — propose those through the inbox and leave them untouched until a
human accepts.

## Pass 3 — discovery

Spend `frontier_searches` searches on work that no band names. This pass is
undirected on purpose. Do not narrow it back to the topics in `core`.

1. Rank Confluence spaces by update volume over the last `sweep_activity_days`
   days. Sample at most `sweep_max_spaces` of them, highest activity first.
2. Skip anything matching `excluded`. Skip spaces already fully covered by
   passes 1 and 2.
3. Prefer breadth over depth. You are looking for the shape of what is moving,
   not a complete reading of any one space.
4. Favor evidence that crosses a product boundary: the same label, term, author,
   or dependency appearing in spaces that have no reason to be related. A single
   busy space is usually just a busy team; the same idea in three unrelated
   spaces is the thing worth recording.

Record what you swept and rejected, not only what you kept. A space you looked
at and dismissed is a result, and writing it down is what stops the next run
from rediscovering the same dead end. Carry that list in the digest under
explored-and-rejected coverage, and consult it before sweeping again.

## Signals

A signal is one observation from one source, with no status and no commitment.
It is the cheap tier, and most discovery output belongs here.

Create each new signal from `templates/signal.md` in `wiki/signals/`. Set `band`
to the pass that found it. Write at most `max_signals_per_run` signals in a
single run; if more qualify, keep the ones that cross the most product
boundaries and say in the digest how many you dropped.

Never inflate a signal into a claim to make it feel more substantial. A signal
that turns out to be load-bearing gets promoted later, by the synthesis pass or
by a human, and records `promoted_to` when it does.

Signals write straight into the wiki. Everything below goes to the inbox first.

## Proposals

Some changes are too consequential for an unattended job to make. Raise these as
`templates/inbox-item.md` in `wiki/inbox/` with `status: pending`, and stop
there:

| Proposal | Why it waits |
| --- | --- |
| A new theme page | A theme asserts that a pattern is real |
| Any change to `core` or `excluded` | These define what the wiki is for |
| A new product page not implied by an accepted topic | Same |

Every proposal must cite the signal or claim IDs that justify it in `evidence`.
A proposal with no evidence is not ready to raise. Before raising one, check the
inbox for an existing pending item and for a rejected item making the same
argument; re-raising something a human already declined is noise, not diligence.

## Claims

Create each new atomic claim from `templates/claim.md`. Preserve history through
reciprocal `supersedes` and `superseded_by` links. Never turn proposal,
candidate, target, expected, or in-progress language into a commitment.

Update only affected product pages, theme pages, `wiki/index.md`, and the
monthly log. When an affected product page is missing, create it from
`templates/product.md` and replace every placeholder. Do not create a theme page
directly; propose it. Preserve existing pages and unrelated files; never
overwrite a page wholesale or create an unaffected page.

## Close out

Run:

```shell
uv run python -m unittest tests.test_lint_wiki -v
uv run python scripts/lint_wiki.py --root .
```

Warnings are expected when signals or proposals are waiting; they are a review
queue, not a failure. Errors are.

Update automation memory with the run date, changed claim IDs, new signal IDs,
raised proposal IDs, the swept-and-rejected list, and baseline. Never stage,
commit, delete, or silently reinterpret evidence.

Lead the user-facing result with changed claims, status, update date, and
citations. Then report discovery separately: what was swept, what was recorded
as a signal, what is waiting in the inbox. End with the Sales Engineer
validation reminder.

## Eligible sources

Confluence pages and Jira issues found through Atlassian Rovo are both valid
sources. For every material claim, record the source title, direct URL,
verified update date, source type (`Confluence` or `Jira`), freshness label,
and evidence status. Signals carry the same citation fields but no freshness
label and no evidence status, because they assert nothing yet.
