# Confluence Research Wiki

Before any ingest, read `wiki/index.md`, the current month's `logs/` file, and
the automation memory when running a daily digest.

Create one immutable raw record per ingest. Verify every cited source update
date. Promote only material, source-grounded changes to claims. A new
conflicting claim must link to the old claim with reciprocal `supersedes` and
`superseded_by` fields. Update only affected product pages, theme pages, and
the index, then append a log entry.

Every claim must record `source_title`, `source_type` (`Confluence` or `Jira`),
and a `freshness` label consistent with `source_updated`: `RECENT` for 0-30
days, `CURRENT WINDOW` for 31-90 days, or
`STALE - VERIFY BEFORE CUSTOMER USE` after 90 days.

A source labeled proposal, candidate, target, expected, or in progress is not
a committed delivery date unless the source explicitly labels it committed,
generally available, scheduled, or a customer commitment.

Do not auto-commit, delete raw records, erase historical claims, or silently
reinterpret evidence. A no-material-change run still receives a raw record and
log entry.
