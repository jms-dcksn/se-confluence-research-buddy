# Synthesis pass contract

This pass runs on `synthesis_day` from `wiki/research-scope.md`, after the daily
digest finishes. It is the only part of the system that can see a trend, because
a trend is not visible in a single run.

**Read the wiki, not Confluence.** This pass performs no Atlassian retrieval.
Its inputs are the signals, claims, themes, questions, and logs already on disk.
If you find yourself searching Confluence, you are running the wrong pass.

Read `AGENTS.md`, `wiki/research-scope.md`, `wiki/index.md`, every file in
`wiki/signals/`, `wiki/claims/`, `wiki/themes/`, `wiki/questions/`, the pending
items in `wiki/inbox/`, and the last four weeks of `logs/`.

## What to look for

Work through these deliberately. Each one finds a different kind of pattern, and
skipping one silently narrows the wiki in exactly the way this system exists to
prevent.

| Lens | Question |
| --- | --- |
| Co-occurrence | Which terms, labels, authors, or dependencies appear across products with no organizational reason to be related? |
| Recurrence | Which observation has now been recorded three or more times, in separate runs, from separate sources? |
| Spike | Which product, space, or term jumped in activity against its own recent baseline? |
| Gap | What appears on three or more product pages but has no theme page? |
| Conflict | Which disagreement between sources has recurred rather than resolved? |
| Absence | Which `core` topic has produced nothing for several weeks? Silence is a finding. |

Three unrelated products doing the same thing is a theme. One product doing
something three times is just that product working. Hold the line there — a
theme that turns out to be one team's activity is worse than no theme, because
it tells the reader a pattern exists when it does not.

## Proposing a theme

A theme is a claim that a pattern is real, so it goes to the inbox and waits.
Never write a theme page directly.

Raise `templates/inbox-item.md` with `proposal_type: theme`, and cite in
`evidence` every signal and claim ID behind it. State in the proposal:

- the pattern, phrased so it could be wrong
- which products it spans, and how directly each is involved
- what would falsify it

Do not propose a theme supported by fewer than three signals or claims, and do
not propose one whose evidence all comes from a single product or a single
author. Check `wiki/inbox/` for a rejected proposal making the same argument
before raising a new one.

When a human accepts a theme proposal, the accepted theme page is created from
`templates/theme.md` with `maturity: emerging`, and every cited signal is marked
`status: promoted` with the theme recorded in `promoted_to`.

## Maintaining themes

Re-ground each existing theme against its evidence:

| Change | When |
| --- | --- |
| `emerging` to `established` | The pattern has held across at least two synthesis passes and is now supported by claims, not only signals |
| `established` to `faded` | No supporting signal or claim in the last 90 days |
| `faded` back to `emerging` | Fresh evidence has arrived |

Record every maturity change in the theme's History section with the date and
what prompted it. Update `last_synthesized` on every theme you examine, whether
or not it changed. Never delete a theme; `faded` is the retirement state, and
the history is the point.

## Open questions

This is what makes the loop compound rather than repeat. A pass that produces no
questions has read the wiki without thinking about it.

Raise a question in `wiki/questions/` from `templates/question.md` whenever:

- a theme's pattern has an obvious next thing to check
- two sources conflict and neither is authoritative
- a signal is interesting but one source is not enough to act on
- a `core` topic has gone quiet and you cannot tell whether the work stopped or
  moved

Questions write directly; they assert nothing. Set `status: answered` and record
`answered_by` when a later claim or signal settles one. Set `status: dropped`,
with the reason in the body, when a question has been searched repeatedly and is
not going to resolve — carrying it forever is noise.

The next daily digest reads open questions as search seeds. Phrase the "what
would answer it" section concretely enough to be searchable, or the question
cannot feed back into retrieval.

## Close out

Update `wiki/index.md`: emerging themes, open questions, and what changed.
Append a log entry recording themes proposed, maturity changes, questions raised,
questions answered or dropped, and signals promoted.

Run:

```shell
uv run python scripts/lint_wiki.py --root .
```

Warnings about long-open questions and unpromoted signals are the backlog this
pass exists to work down. Read them as a worklist, not a failure.

Report to the user: proposed themes and their evidence first, then maturity
changes, then new questions. Say plainly that a proposed theme is an argument
awaiting their judgment, not a finding. End with the Sales Engineer validation
reminder.
