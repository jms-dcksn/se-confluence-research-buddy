# Confluence Research Wiki

Open this folder in Obsidian. Review `raw/confluence/` before accepting changes
to `wiki/`.

## Where to look

| Folder | What it holds | Who writes it |
| --- | --- | --- |
| `wiki/claims/` | Dated, cited, customer-facing facts | The digest |
| `wiki/signals/` | One-source observations that assert nothing yet | The digest |
| `wiki/inbox/` | Proposals waiting on your decision | The digest raises, you decide |
| `wiki/themes/` | Named cross-product patterns | You, by accepting a proposal |
| `wiki/questions/` | What the wiki does not know yet | The synthesis pass raises, the digest chases |
| `wiki/products/` | Per-topic pages | The digest, for accepted topics |

Start each review in `wiki/inbox/`. The digest cannot create a theme or change
what the wiki is scoped to; it can only ask.

## Rhythm

The daily digest keeps known work current and spends part of every run
searching outside the topic list. On `synthesis_day` it also runs
`contracts/synthesis-pass.md`, which reads this wiki rather than Confluence and
looks for patterns across products. Themes are proposed only by that pass, and
only you can accept one.

`wiki/research-scope.md` holds the scope bands and the discovery budget. Edit
`core` and `excluded` freely — they are yours. `adjacent` is maintained by the
digest, with every change recorded in the discovery log at the bottom of that
page.

## Checks

```shell
uv run python scripts/lint_wiki.py --root .
```

Errors mean the wiki's contracts are broken. Warnings mean something is waiting
on you — a signal open too long, a proposal pending too long — and do not fail
the run. Run this before committing reviewed updates.
