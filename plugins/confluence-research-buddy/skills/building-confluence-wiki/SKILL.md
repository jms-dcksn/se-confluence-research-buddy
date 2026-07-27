---
name: building-confluence-wiki
description: Use when creating, customizing, validating, or scheduling an Obsidian-compatible local wiki for recurring Confluence research and digest tracking.
---

# Building a Confluence Research Wiki

## Core principle

Create a citation-first local wiki without overwriting the user's work. Treat
setup validation, live Atlassian retrieval, and human acceptance as separate
checks.

## Setup contract

Collect or confirm these inputs before changing files:

| Input | Required detail |
| --- | --- |
| Destination | Absolute local folder |
| Topics | Product, program, or theme names |
| Ingest mode | Manual only or scheduled digest |
| Schedule | Digest time and timezone, if scheduled |

Confirm Atlassian Rovo is installed and connected before setup. If it is
unavailable, stop and explain that the Atlassian Rovo plugin must be installed
and connected. Do not substitute unverified snippets or another connector.

Confluence pages and Jira issues retrieved through Atlassian Rovo are both
eligible sources. Every material claim must include a source title, direct URL,
verified last-updated date, source type (`Confluence` or `Jira`), freshness
label, and evidence status.

## Build the wiki

1. Inspect the destination, including hidden files, before copying anything.
2. In the setup plan, say: `Use the bundled generic wiki starter.` Resolve it
   at `../../assets/wiki-starter/`, relative to this skill, then compare its
   relative paths with the destination.
3. Preserve every existing file. Copy only non-conflicting starter files. If a
   destination path already exists, show the conflict and ask whether to keep,
   rename, or explicitly replace it; do not overwrite by default.
4. Create one `wiki/products/<topic-slug>.md` page per topic from
   `templates/product.md`. Replace placeholders and add the pages to
   `wiki/index.md`.
5. Populate `wiki/research-scope.md` with the exact topic names in order,
   absolute destination, digest time, timezone, and setup date. For manual-only
   setup, use `manual-only` for digest time and timezone. Leave no setup
   placeholder in the page.
6. Replace `last_reviewed: YYYY-MM-DD` in `wiki/index.md` with the setup date.
   Initialize `logs/YYYY-MM.md` for the current month with a Markdown heading
   when it is absent. Preserve and inspect an existing monthly log instead of
   replacing it. Apply the same conflict rule to every setup edit.
7. From the destination, run `git rev-parse --is-inside-work-tree`. Run
   `git init` only when that check fails. Explain Git plainly as local change
   history and a safety net; initialization does not publish files or commit
   anything.
8. Run:

   ```powershell
   uv run python -m unittest tests.test_lint_wiki -v
   uv run python scripts/lint_wiki.py --root .
   ```

   Report these as local structural validation, not proof of a successful live
   Atlassian ingest.
9. Tell the user to open Obsidian, choose **Open folder as vault**, and select
   the destination.

## Optional scheduled digest

For manual-only setup, stop after validation and do not read the scheduling
reference.

When scheduling is requested:

1. Read `references/scheduled-digest.md`.
2. Reconfirm the local time, timezone, topics, destination, and Atlassian Rovo
   connection. Do not infer timezone from the machine or silently select one.
3. Verify `wiki/research-scope.md`, `wiki/index.md`, and the current monthly log
   contain the confirmed first-run values before creating the schedule.
4. Build the automation prompt as this exact shape:

   ```text
   Research topics (exact, in this order): <topic 1>; <topic 2>
   Working destination (exact): <absolute destination>
   Digest time (exact): <HH:MM>
   Timezone (exact): <IANA timezone>

   <the complete text of references/scheduled-digest.md>
   ```

   Interpolate literal values, not placeholders or "configured topics." Copy
   the complete reference text into the prompt; do not give the automation only
   a pointer to the file.
5. Search for and use the Codex automation tool. Create exactly one recurring
   automation with the destination as its working folder and the constructed
   prompt. Never create a live schedule during a description-only or
   validation scenario.
6. Read back the created automation and verify the exact topics, destination,
   digest time, timezone, and complete job contract. Report the schedule and
   timezone. Do not create a second automation to compensate for uncertainty;
   inspect the existing result instead.

## Handoff

Explain that automation output is a review queue, not accepted truth. A human
must inspect citations, dates, statuses, conflicts, and generated diffs before
committing or using findings with customers. The automation must never stage,
commit, or delete files.

## Common mistakes

| Mistake | Correction |
| --- | --- |
| Copying over an occupied folder | Compare paths first; ask on each conflict |
| Assuming 9:00 means local time | Confirm an explicit timezone |
| Running `git init` automatically | Initialize only after `git rev-parse` fails |
| Treating lint as retrieval proof | Label it local structural validation |
| Accepting generated updates | Require human evidence and diff review |
