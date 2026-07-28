# Confluence Research Buddy

Confluence Research Buddy helps Sales Engineers research internal information
or build a new Obsidian-compatible research wiki. You do not need an existing
wiki.

## Install and start

### Easy route: ask Codex in chat

In a Codex chat, send:

> Install the plugin from https://github.com/jms-dcksn/se-confluence-research-buddy.git.

Codex can clone the repository and install the plugin for you. Approve any
requested clone or plugin-install permission, then connect Atlassian Rovo.

### Deterministic terminal route

Run these commands in Windows PowerShell, macOS Terminal, or Linux shells:

```shell
git clone https://github.com/jms-dcksn/se-confluence-research-buddy.git
cd se-confluence-research-buddy
codex plugin marketplace add .
codex plugin add confluence-research-buddy@confluence-research-tools
```

Install and connect Atlassian Rovo in Codex, then verify the plugin:

```shell
codex plugin list
```

Look for `confluence-research-buddy@confluence-research-tools` with an enabled
status. Start a new Codex task and try one of these prompts:

   - Find recent Confluence updates about this product.
   - Research this roadmap topic with citations.
   - Build my Confluence research wiki.

The full wiki path needs Obsidian, Git, and `uv`. Its starter requires Python
3.11 or newer; `uv` can obtain the needed Python runtime. If the plugin is
missing from `codex plugin list`, run `codex plugin marketplace list`, confirm
that `confluence-research-tools` points to the cloned folder, and repeat the
two Codex plugin commands from that folder.

## Before customer use

Confluence pages and Jira issues are both valid Atlassian Rovo evidence. Every
material claim needs its direct source URL, verified update date, source type,
freshness label, and status. The Sales Engineer must validate findings before
customer use.
