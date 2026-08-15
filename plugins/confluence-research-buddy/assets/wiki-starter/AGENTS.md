# Confluence Research Wiki

Before any ingest, read `wiki/index.md`, `wiki/research-scope.md`, the current
month's `logs/` file, and the automation memory when running a daily digest.

Create one immutable raw record per ingest. Verify every cited source update
date. Promote only material, source-grounded changes to claims. A new
conflicting claim must link to the old claim with reciprocal `supersedes` and
`superseded_by` fields. Update only affected product pages, theme pages, and
the index, then append a log entry.

## Two layers, two half-lives

| Layer | Node | Contract |
| --- | --- | --- |
| Evidence | `wiki/claims/` | Dated, cited, status-classified, expires at 90 days. Customer-facing. |
| Discovery | `wiki/signals/` | One observation, one source. No status, no freshness label, no expiry. Asserts nothing. |
| Concept | `wiki/themes/` | A named pattern spanning products. Carries its emergence evidence and a maturity, does not expire, but goes stale without re-grounding. |
| Agenda | `wiki/questions/` | What the wiki does not know. Consumed by the next digest as search seeds. |

Keep them separate. A signal is not a weak claim, and a claim is not a
well-supported signal. Never upgrade a signal by adding a status to it; promote
it deliberately and record `promoted_to`.

Every claim must record `source_title`, `source_type` (`Confluence` or `Jira`),
and a `freshness` label consistent with `source_updated`: `RECENT` for 0-30
days, `CURRENT WINDOW` for 31-90 days, or
`STALE - VERIFY BEFORE CUSTOMER USE` after 90 days.

A source labeled proposal, candidate, target, expected, or in progress is not
a committed delivery date unless the source explicitly labels it committed,
generally available, scheduled, or a customer commitment.

## What may be written unattended

Write directly: claims, signals, questions, product pages for accepted topics,
the `adjacent` band, the discovery log, logs, and raw records. Theme maturity
changes and `last_synthesized` updates on existing themes are also direct; only
creating a theme requires a decision.

Propose through `wiki/inbox/` and leave untouched: new theme pages, any change
to `core` or `excluded`, and product pages for topics nobody accepted. Every
proposal cites the signal or claim IDs behind it.

## Exploration is part of the job

Searching only the `core` band is an incomplete run. Spend the discovery budget
in `wiki/research-scope.md` on work outside every band, favor evidence that
recurs across unrelated products, and record what was swept and dismissed as
well as what was kept.

Read open questions before searching and append to them after. A run that
answers nothing and asks nothing has repeated the previous run rather than
built on it.

## Trends are found weekly, not daily

A daily run cannot see a pattern; it sees one day. The synthesis pass on
`synthesis_day` reads the accumulated wiki rather than Confluence and is the
only place themes are proposed. Three unrelated products doing the same thing
is a theme. One product doing something three times is that product working.

Do not auto-commit, delete raw records, erase historical claims, re-raise a
proposal a human rejected, or silently reinterpret evidence. A no-material-change
run still receives a raw record and log entry.
