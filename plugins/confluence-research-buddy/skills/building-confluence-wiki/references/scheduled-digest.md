# Scheduled digest contract

Before retrieval, read `AGENTS.md`, `wiki/research-scope.md`, `wiki/index.md`,
the current month's log, and the automation memory when it exists. A missing
memory record is valid on the first run; initialize it after completing that
run. Verify that the exact
topics, destination, digest time, and timezone embedded above this contract
match `wiki/research-scope.md`; stop and report the mismatch instead of
guessing.

Search only the exact topics embedded above this contract through Atlassian
Rovo. Prioritize sources updated within seven days. Verify every source update
date. Label anything older than 90 days or missing a verified date
`STALE - VERIFY BEFORE CUSTOMER USE`.

Create at most one `raw/confluence/YYYY-MM-DD-daily-digest.md` per calendar
date. If a completed record already exists, verify it and exit without creating
another. Create a new digest from `templates/digest.md` and replace every
placeholder. Record material changes and explicit no-change coverage.

Create each new atomic claim from `templates/claim.md`. Preserve history through
reciprocal `supersedes` and `superseded_by` links. Never turn proposal,
candidate, target, expected, or in-progress language into a commitment.

Update only affected product pages, theme pages, `wiki/index.md`, and the
monthly log. When an affected product or theme page is missing, create it from
`templates/product.md` or `templates/theme.md` and replace every placeholder.
Preserve existing pages and unrelated files; never overwrite a page wholesale
or create an unaffected page.

Run:

```shell
uv run python -m unittest tests.test_lint_wiki -v
uv run python scripts/lint_wiki.py --root .
```

Update automation memory with the run date, changed claim IDs, and baseline.
Never stage, commit, delete, or silently reinterpret evidence.

Lead the user-facing result with changed claims, status, update date, and
citations. End with the Sales Engineer validation reminder.

## Eligible sources

Confluence pages and Jira issues found through Atlassian Rovo are both valid
sources. For every material claim, record the source title, direct URL,
verified update date, source type (`Confluence` or `Jira`), freshness label,
and evidence status.
