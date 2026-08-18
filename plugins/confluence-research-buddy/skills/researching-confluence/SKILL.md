---
name: researching-confluence
description: Use when researching internal Confluence product information, recent updates, roadmap items, capabilities, delivery status, or broad company topics through Atlassian Rovo.
---

# Researching Confluence

## Core principle

Confluence and Jira are evidence, not truth. Search before answering, verify
source dates, cite every material claim, and leave customer judgment to the
Sales Engineer.

## Choose a mode

| Request | Mode |
| --- | --- |
| What changed, latest, recent, this week | Recent updates |
| Everything about, investigate, compare, roadmap, capability | Comprehensive research |

For recent updates, search the last seven days first and expand only as far as
90 days. Define the important areas in scope, then report both material changes
and explicit no-confirmed-change coverage for every area searched.

For comprehensive research, search the topic, product names, synonyms, and
related programs. Inspect relevant Confluence pages and Jira issues rather than
relying on snippets. Compare sources by ownership and purpose, directness,
update date, delivery language, and conflict. Identify evidence gaps and
inaccessible sources.

## Evidence rules

Use the Atlassian Rovo connector as the only retrieval source. It is exposed
differently per host:

| Host | Connector | Availability check |
| --- | --- | --- |
| Claude Code | The `claude.ai` Atlassian Rovo connector, added in the Claude Desktop app or on claude.ai. This plugin ships no MCP server of its own. A connector the user added by hand works the same way. | A real call to `getAccessibleAtlassianResources` returns a cloud ID. |
| Codex | Atlassian Rovo plugin | The Rovo plugin is installed and connected |

Recognize the tools by their bare Atlassian names — `getAccessibleAtlassianResources`,
`searchConfluenceUsingCql`, `getConfluencePage` — and never by their server prefix.
The prefix is assigned by the host, and a `claude.ai` connector namespaces its tools
under an opaque connector identifier rather than the word `atlassian`. Matching on
the prefix reports a working connector as missing, and the stop rule below then
aborts a run that had every tool it needed.

A connector reporting healthy is not an availability check. The transport handshake
can succeed while the server advertises no tools at all, which is what an expired or
revoked authorization looks like from this side. Only a successful call counts.

If no Rovo tools are available, stop and explain how to connect one: in Claude
Code, add the Atlassian Rovo connector in the Claude Desktop app or on claude.ai
under Settings, then Connectors, and start a new session so its tools load; in
Codex, install and connect the Atlassian Rovo plugin. Do not substitute web
search, another connector, or model knowledge.

Treat Confluence pages and Jira issues as eligible evidence. For every material
claim, record the source title, identify the source type as `Confluence` or
`Jira`, verify the source's last-updated date, and include its direct URL. Apply
the same freshness, evidence-status, and commitment-language rules to both
source types.

Label freshness:

- 0-30 days: `RECENT`
- 31-90 days: `CURRENT WINDOW`
- More than 90 days or unknown date: `STALE - VERIFY BEFORE CUSTOMER USE`

Historical sources may provide context but cannot establish current behavior.
A newer source validates an older claim only when it explicitly confirms it.

Classify evidence as `current`, `at-risk`, `proposed`, `superseded`, or `stale`.
Proposal, candidate, target, expected, and in-progress language is not a
commitment. Only explicit committed, GA, scheduled, or customer-commitment
language supports a delivery commitment. Classify ordinary `In Progress` work
as `proposed`; use `at-risk` only when the source explicitly reports delivery
risk.

## Authority and access

Explain which source is strongest for the claim and why. A direct release,
availability, or support record normally carries more authority for shipped
behavior than a planning page or Jira activity, but authority and recency do
not replace visible evidence. Show unresolved conflicts rather than selecting a
winner without support.

When a page is inaccessible but a search result is visible:

1. Use only the visible title, direct result URL, verified date, and snippet.
2. Label it `UNVERIFIED - VISIBLE SNIPPET ONLY`.
3. Do not infer or paraphrase the inaccessible page body, and do not use the
   result alone to classify a claim as `current`.
4. Name the permission gap and the access or alternate source needed.

`UNVERIFIED - VISIBLE SNIPPET ONLY` is an access label, not a sixth evidence
status. Record the inaccessible result under conflicts and gaps rather than
inventing a material claim for the evidence table. Keep every claim's evidence
status limited to the five values above.

If the result does not show a verified update date, apply
`STALE - VERIFY BEFORE CUSTOMER USE`.

## Response contract

Return:

1. Direct answer.
2. Evidence table: claim, evidence status, source type, source updated,
   freshness, access or evidence limit, and a titled direct citation.
3. Conflicts, source-authority comparison, permission gaps, missing
   information, and recent-mode no-change coverage.
4. Customer-use check.

End by stating that Confluence and Jira may be incomplete or outdated and the
Sales Engineer must validate the findings before using them with customers.
