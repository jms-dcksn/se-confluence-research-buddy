---
name: building-confluence-wiki
description: Use when creating, customizing, validating, or scheduling an Obsidian-compatible local wiki for recurring Confluence research, cross-product discovery, and digest tracking.
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
| Core topics | Product, program, or theme names. The standing watchlist, not a ceiling. |
| Excluded areas | Spaces or topics the sweep must never surface. Optional; ask, do not assume. |
| Discovery budget | Searches per run spent outside every band. Default 5. |
| Instance size | Rough number of active Confluence spaces, used to set the sweep caps |
| Synthesis day | Weekday the trend pass runs. Default Sunday. |
| Ingest mode | Manual only or scheduled digest |
| Schedule | Digest time and timezone, if scheduled |

Explain that core topics are the floor, not the ceiling: the digest also
searches outward and records what it finds as signals, so under-listing here is
safe and over-listing narrows the wiki. If the user gives no excluded areas,
leave the band empty rather than inventing entries.

Set the sweep caps from the instance size. `sweep_max_spaces` defaults to 25;
raise it toward full coverage on a small instance, and lower it on a large or
noisy one so a single run stays bounded. Tell the user which values you chose
and that they can edit them in `wiki/research-scope.md` at any time.

### Check the Atlassian connector first

This plugin ships no MCP server of its own. Retrieval comes from a connector the
user owns, so confirm it works **before** collecting inputs or touching files. A
wiki built against a dead connector is a folder of empty templates, and the user
will not find out until the first digest.

Check it by **calling** `getAccessibleAtlassianResources` and getting a cloud ID
back. That is the only check that means anything:

- Find the tools by their bare Atlassian names — `getAccessibleAtlassianResources`,
  `searchConfluenceUsingCql`, `getConfluencePage`. Never by server prefix. The
  prefix is assigned by the host, and a `claude.ai` connector namespaces its tools
  under an opaque connector identifier rather than the word `atlassian`, so
  matching on the prefix reads a working connector as absent.
- A connector reporting connected is not evidence. The transport handshake can
  succeed while the server advertises zero tools, which is what an expired or
  revoked authorization looks like from this side.

If the call does not return a cloud ID, stop and tell the user how to fix it. Do
not build the wiki, and do not substitute unverified snippets or another
connector:

| Host | How the user connects Atlassian |
| --- | --- |
| Claude Code | Add the **Atlassian Rovo connector** in the Claude Desktop app or on claude.ai — Settings, then Connectors. Configuring it there applies it across sessions, including Desktop scheduled tasks. Then start a new session so the tools load. |
| Codex | Install and connect the Atlassian Rovo plugin. |

Report which site the cloud ID belongs to, so the user can catch being connected
to the wrong Atlassian instance while everything still looks healthy.

Confluence pages and Jira issues retrieved through Atlassian Rovo are both
eligible sources. Every material claim must include a source title, direct URL,
verified last-updated date, source type (`Confluence` or `Jira`), freshness
label, and evidence status.

## Build the wiki

1. Inspect the destination, including hidden files, before copying anything.
2. In the setup plan, say: `Use the bundled generic wiki starter.` Resolve it
   at `assets/wiki-starter/` under the plugin root — in Claude Code that is
   `${CLAUDE_PLUGIN_ROOT}/assets/wiki-starter/`; otherwise resolve
   `../../assets/wiki-starter/` relative to this skill file. Do not assume the
   plugin is installed at a fixed path. Then compare its relative paths with
   the destination.
3. Preserve every existing file. Copy only non-conflicting starter files. If a
   destination path already exists, show the conflict and ask whether to keep,
   rename, or explicitly replace it; do not overwrite by default.
4. Create one `wiki/products/<topic-slug>.md` page per topic from
   `templates/product.md`. Replace placeholders and add the pages to
   `wiki/index.md`.
5. Populate `wiki/research-scope.md`: the exact topic names in order under
   `core`, any excluded areas under `excluded`, an empty `adjacent` band, the
   discovery budget and sweep caps, the synthesis day, absolute destination,
   digest time, timezone, and setup date. For manual-only setup, use `manual-only` for
   digest time and timezone. Leave no setup placeholder in the page.
6. Replace `last_reviewed: YYYY-MM-DD` in `wiki/index.md` with the setup date.
   Initialize `logs/YYYY-MM.md` for the current month with a Markdown heading
   when it is absent. Preserve and inspect an existing monthly log instead of
   replacing it. Apply the same conflict rule to every setup edit.
7. From the destination, run `git rev-parse --is-inside-work-tree`. Run
   `git init` only when that check fails. Explain Git plainly as local change
   history and a safety net; initialization does not publish files or commit
   anything.
8. Run:

   ```shell
   uv run python -m unittest tests.test_lint_wiki -v
   uv run python scripts/lint_wiki.py --root .
   ```

   Report these as local structural validation, not proof of a successful live
   Atlassian ingest.
9. Tell the user to open Obsidian, choose **Open folder as vault**, and select
   the destination.

## Optional scheduled digest

For manual-only setup, stop after validation and do not read the scheduling
reference. Mention that `contracts/synthesis-pass.md`, copied into the
destination with the starter, can still be run by hand whenever the user wants a
trend review, since it reads the wiki rather than Confluence.

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
5. Create exactly one recurring automation, with the destination as its working
   folder and the constructed prompt as its instruction. Pick the scheduler
   that fits the host:

   | Host | Scheduler | Note |
   | --- | --- | --- |
   | Claude Code desktop | Desktop scheduled task | Preferred. Runs locally, reaches the wiki folder, persists across restarts. |
   | Claude Code CLI | `CronCreate` | Session-scoped and expires after seven days. Offer it only as a stopgap and say so plainly. |
   | Codex | Codex automation tool | |

   The digest reads and writes a local folder, so never schedule it on a
   cloud runner that starts from a fresh clone. Never create a live schedule
   during a description-only or validation scenario.
6. Read back the created automation and verify the exact topics, destination,
   digest time, timezone, and complete job contract. Report the schedule and
   timezone. Do not create a second automation to compensate for uncertainty;
   inspect the existing result instead.

## Handoff

Explain that automation output is a review queue, not accepted truth. A human
must inspect citations, dates, statuses, conflicts, and generated diffs before
committing or using findings with customers. The automation must never stage,
commit, or delete files.

Walk the user through the two things the digest will produce beyond claims:

- `wiki/signals/` fills on its own with one-source observations. Nothing there
  is asserted or customer-safe. Recurring signals are the raw material for a
  theme.
- `wiki/inbox/` holds proposals the digest is not allowed to act on: new
  themes, and any change to `core` or `excluded`. Nothing there takes effect
  until the user accepts it, and the linter warns once an item has been pending
  for a month.

- `wiki/questions/` is the research agenda. The digest reads open questions as
  search seeds and appends what it searched, so the wiki directs its own next
  run instead of restarting from the topic list each time.

Say plainly that the digest will edit the `adjacent` band and the discovery log
by itself, and will never touch `core` or `excluded`. Point at the discovery
log as the place to see what it has been steering toward.

Explain the weekly rhythm: the daily run keeps known work current, and on the
synthesis day it also reads the accumulated wiki — not Confluence — looking for
patterns across products. Themes come only from that pass, and arrive as
proposals in the inbox. Tell the user that an accepted theme is where the
"new topic for the wiki" actually gets named, and that rejecting one is a
normal outcome, not a failure.

## Common mistakes

| Mistake | Correction |
| --- | --- |
| Copying over an occupied folder | Compare paths first; ask on each conflict |
| Assuming 9:00 means local time | Confirm an explicit timezone |
| Running `git init` automatically | Initialize only after `git rev-parse` fails |
| Scheduling the digest on a cloud runner | The wiki is local; use a scheduler with local file access |
| Hardcoding the starter path | Resolve it from the plugin root, which moves on update |
| Treating lint as retrieval proof | Label it local structural validation |
| Accepting generated updates | Require human evidence and diff review |
| Treating core topics as the whole scope | They are the floor; the discovery budget searches past them |
| Editing `core` or `excluded` unattended | Raise an inbox proposal and wait |
| Writing a theme page from one run | Themes assert a pattern; propose, do not create |
| Recording a signal as a claim | Signals carry no status and expire nothing |
| Calling one product's activity a theme | A theme spans products; three sightings in one team is not one |
| Running synthesis against Confluence | It reads the wiki; retrieval belongs to the daily passes |
| Deleting a theme that stopped moving | Demote it to `faded`; the history is the point |
