# Confluence Research Buddy

Confluence Research Buddy helps Sales Engineers research internal information
or build a new Obsidian-compatible research wiki. You do not need an existing
wiki.

## Install and start

1. Download or clone the repository containing this plugin.
2. Install and connect Atlassian Rovo in Codex.
3. Open a terminal in the downloaded folder and add its marketplace. The
   commands in these steps work in Windows PowerShell, macOS Terminal, and
   Linux shells:

   ```shell
   codex plugin marketplace add .
   ```

4. Install the plugin:

   ```shell
   codex plugin add confluence-research-buddy@confluence-research-tools
   ```

5. Verify the install:

   ```shell
   codex plugin list
   ```

   Look for `confluence-research-buddy@confluence-research-tools` with an
   enabled status.
6. Start a new Codex task and try one of these prompts:

   - Find recent Confluence updates about this product.
   - Research this roadmap topic with citations.
   - Build my Confluence research wiki.

The full wiki path needs Obsidian, Git, and `uv`. Its starter requires Python
3.11 or newer; `uv` can obtain the needed Python runtime. If the plugin is
missing from `codex plugin list`, run `codex plugin marketplace list`, confirm
that `confluence-research-tools` points to the downloaded folder, and repeat
steps 3 and 4 from that folder.

## Before customer use

Confluence pages and Jira issues are both valid Atlassian Rovo evidence. Every
material claim needs its direct source URL, verified update date, source type,
freshness label, and status. The Sales Engineer must validate findings before
customer use.
