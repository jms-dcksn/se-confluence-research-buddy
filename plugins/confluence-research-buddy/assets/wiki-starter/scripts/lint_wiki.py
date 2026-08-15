"""Validate citation, history, and navigation contracts in the Markdown wiki."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
import sys


REQUIRED_FIELDS = {
    "id",
    "title",
    "products",
    "themes",
    "claim_type",
    "status",
    "source_updated",
    "source_url",
    "evidence_note",
    "source_record",
    "supersedes",
    "superseded_by",
    "confidence",
}
CURRENT_EVIDENCE_FIELDS = {"source_title", "source_type", "freshness"}
VALID_STATUSES = {"current", "at-risk", "proposed", "superseded", "stale"}
CUSTOMER_RELEVANT_STATUSES = {"current", "at-risk", "proposed"}
VALID_SOURCE_TYPES = {"Confluence", "Jira"}
UNCONFIGURED_VALUES = {"", "TO_BE_CONFIGURED", "YYYY-MM-DD"}
WIKILINK_PATTERN = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")

SIGNAL_REQUIRED_FIELDS = {
    "id",
    "title",
    "observed",
    "band",
    "source_title",
    "source_type",
    "source_updated",
    "source_url",
    "status",
    "promoted_to",
}
VALID_SIGNAL_STATUSES = {"open", "promoted", "dismissed"}
VALID_BANDS = {"core", "adjacent", "frontier"}
INBOX_REQUIRED_FIELDS = {"id", "proposal_type", "title", "raised", "status", "evidence"}
VALID_INBOX_STATUSES = {"pending", "accepted", "rejected"}
VALID_PROPOSAL_TYPES = {"theme", "scope-change", "product"}
THEME_REQUIRED_FIELDS = {"title", "kind", "maturity", "last_reviewed", "emerged_from"}
VALID_MATURITIES = {"emerging", "established", "faded"}
MIN_THEME_EVIDENCE = 3
QUESTION_REQUIRED_FIELDS = {"id", "title", "raised", "status", "answered_by"}
VALID_QUESTION_STATUSES = {"open", "answered", "dropped"}
SCOPE_BUDGET_FIELDS = (
    "frontier_searches",
    "sweep_activity_days",
    "sweep_max_spaces",
    "max_signals_per_run",
)

# Backlog thresholds. These raise warnings, never errors: an unattended
# backlog is a review signal, not a broken wiki.
STALE_SIGNAL_DAYS = 45
STALE_INBOX_DAYS = 30
STALE_QUESTION_DAYS = 60
UNSYNTHESIZED_THEME_DAYS = 90


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    message: str
    severity: str = "error"


def _parse_value(value: str) -> object:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [item.strip().strip('"\'') for item in inner.split(",")]
    return value.strip('"\'')


def parse_frontmatter(path: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}

    frontmatter: dict[str, object] = {}
    active_list_key: str | None = None
    for line in lines[1:]:
        if line.strip() == "---":
            return frontmatter
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if active_list_key and line.lstrip().startswith("- "):
            value = line.lstrip()[2:].strip().strip('"\'')
            current = frontmatter[active_list_key]
            if isinstance(current, list):
                current.append(value)
            continue
        if ":" not in line:
            return {}
        key, value = line.split(":", 1)
        key = key.strip()
        if value.strip():
            frontmatter[key] = _parse_value(value)
            active_list_key = None
        else:
            frontmatter[key] = []
            active_list_key = key
    return {}


def _issue(path: Path, message: str, severity: str = "error") -> ValidationIssue:
    return ValidationIssue(path=path, message=message, severity=severity)


def _warn(path: Path, message: str) -> ValidationIssue:
    return _issue(path, message, severity="warning")


def _as_list(value: object) -> list[str]:
    return value if isinstance(value, list) else []


def _wikilinks(path: Path) -> list[str]:
    return [match.group(1).strip() for match in WIKILINK_PATTERN.finditer(path.read_text(encoding="utf-8"))]


def _expected_freshness(source_date: date, today: date) -> str:
    age_days = (today - source_date).days
    if age_days <= 30:
        return "RECENT"
    if age_days <= 90:
        return "CURRENT WINDOW"
    return "STALE - VERIFY BEFORE CUSTOMER USE"


def _is_configured_text(value: object) -> bool:
    return isinstance(value, str) and value.strip() not in UNCONFIGURED_VALUES


def _is_configured_date(value: object) -> bool:
    if not _is_configured_text(value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _validate_setup(wiki_root: Path) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    index_path = wiki_root / "index.md"
    if index_path.exists():
        index = parse_frontmatter(index_path)
        if not _is_configured_date(index.get("last_reviewed")):
            issues.append(
                _issue(
                    index_path,
                    "last_reviewed must be a configured YYYY-MM-DD date",
                )
            )

    scope_path = wiki_root / "research-scope.md"
    if scope_path.exists():
        scope = parse_frontmatter(scope_path)
        # `topics` is the pre-band field name, still accepted so wikis built
        # before scope bands existed keep linting clean.
        core_key = "core" if "core" in scope else "topics"
        core = _as_list(scope.get(core_key))
        if not core or any(not _is_configured_text(topic) for topic in core):
            issues.append(
                _issue(
                    scope_path,
                    f"{core_key} must contain at least one configured topic",
                )
            )
        for band in ("adjacent", "excluded"):
            if band in scope and not isinstance(scope[band], list):
                issues.append(_issue(scope_path, f"{band} must be a list"))
        for field in SCOPE_BUDGET_FIELDS:
            if field not in scope:
                continue
            try:
                budget = int(str(scope[field]))
            except (TypeError, ValueError):
                issues.append(_issue(scope_path, f"{field} must be a whole number"))
            else:
                if budget < 0:
                    issues.append(_issue(scope_path, f"{field} must not be negative"))
        for field in ("destination", "timezone", "digest_time"):
            if not _is_configured_text(scope.get(field)):
                issues.append(_issue(scope_path, f"{field} must be configured"))
        if not _is_configured_date(scope.get("last_configured")):
            issues.append(
                _issue(
                    scope_path,
                    "last_configured must be a configured YYYY-MM-DD date",
                )
            )
    return issues


def _validate_signals(wiki_root: Path, today: date) -> tuple[list[ValidationIssue], set[str]]:
    """Signals are cheap one-source observations, so they are held to a
    lighter contract than claims: cited and dated, but never status-classified
    and never expiring. An unpromoted backlog warns instead of failing."""
    issues: list[ValidationIssue] = []
    seen: set[str] = set()

    for path in sorted((wiki_root / "signals").glob("*.md")):
        metadata = parse_frontmatter(path)
        for field in sorted(SIGNAL_REQUIRED_FIELDS - metadata.keys()):
            issues.append(_issue(path, f"missing required field: {field}"))

        signal_id = metadata.get("id")
        if not isinstance(signal_id, str) or not signal_id:
            issues.append(_issue(path, "id must be a non-empty string"))
            continue
        if signal_id in seen:
            issues.append(_issue(path, f"duplicate signal id: {signal_id}"))
            continue
        seen.add(signal_id)

        status = metadata.get("status")
        if "status" in metadata and status not in VALID_SIGNAL_STATUSES:
            issues.append(_issue(path, f"invalid signal status: {status}"))

        band = metadata.get("band")
        if "band" in metadata and band not in VALID_BANDS:
            issues.append(_issue(path, f"invalid band: {band}"))

        if "source_type" in metadata and metadata["source_type"] not in VALID_SOURCE_TYPES:
            issues.append(_issue(path, "source_type must be Confluence or Jira"))

        source_url = metadata.get("source_url")
        if not isinstance(source_url, str) or not source_url.startswith("https://"):
            issues.append(_issue(path, "source_url must begin with https://"))

        try:
            observed = date.fromisoformat(str(metadata.get("observed")))
        except ValueError:
            issues.append(_issue(path, "observed must be YYYY-MM-DD"))
        else:
            if status == "open" and (today - observed).days > STALE_SIGNAL_DAYS:
                issues.append(
                    _warn(
                        path,
                        f"signal has been open for more than {STALE_SIGNAL_DAYS} days; "
                        "promote or dismiss it",
                    )
                )

        try:
            date.fromisoformat(str(metadata.get("source_updated")))
        except ValueError:
            issues.append(_issue(path, "source_updated must be YYYY-MM-DD"))

        if status == "promoted" and not _as_list(metadata.get("promoted_to")):
            issues.append(_issue(path, "promoted signal must record promoted_to"))

    return issues, seen


def _validate_inbox(wiki_root: Path, today: date) -> list[ValidationIssue]:
    """Inbox items are proposals awaiting a human decision. They gate the
    consequential edits — new themes and scope changes — that the digest is
    not allowed to make on its own."""
    issues: list[ValidationIssue] = []
    seen: set[str] = set()

    for path in sorted((wiki_root / "inbox").glob("*.md")):
        metadata = parse_frontmatter(path)
        for field in sorted(INBOX_REQUIRED_FIELDS - metadata.keys()):
            issues.append(_issue(path, f"missing required field: {field}"))

        item_id = metadata.get("id")
        if not isinstance(item_id, str) or not item_id:
            issues.append(_issue(path, "id must be a non-empty string"))
            continue
        if item_id in seen:
            issues.append(_issue(path, f"duplicate inbox id: {item_id}"))
            continue
        seen.add(item_id)

        status = metadata.get("status")
        if "status" in metadata and status not in VALID_INBOX_STATUSES:
            issues.append(_issue(path, f"invalid inbox status: {status}"))

        proposal_type = metadata.get("proposal_type")
        if "proposal_type" in metadata and proposal_type not in VALID_PROPOSAL_TYPES:
            issues.append(_issue(path, f"invalid proposal_type: {proposal_type}"))

        if "evidence" in metadata and not _as_list(metadata.get("evidence")):
            issues.append(_issue(path, "proposal must cite at least one signal or claim"))

        try:
            raised = date.fromisoformat(str(metadata.get("raised")))
        except ValueError:
            issues.append(_issue(path, "raised must be YYYY-MM-DD"))
        else:
            if status == "pending" and (today - raised).days > STALE_INBOX_DAYS:
                issues.append(
                    _warn(
                        path,
                        f"proposal has been pending for more than {STALE_INBOX_DAYS} days",
                    )
                )

    return issues


def _validate_themes(wiki_root: Path, today: date) -> list[ValidationIssue]:
    """A theme asserts that a pattern spans products, so it must carry the
    evidence that made it one. Unlike a claim it does not expire, but it does
    go stale: an un-resynthesized theme warns rather than fails."""
    issues: list[ValidationIssue] = []

    for path in sorted((wiki_root / "themes").glob("*.md")):
        metadata = parse_frontmatter(path)
        for field in sorted(THEME_REQUIRED_FIELDS - metadata.keys()):
            issues.append(_issue(path, f"missing required field: {field}"))

        maturity = metadata.get("maturity")
        if "maturity" in metadata and maturity not in VALID_MATURITIES:
            issues.append(_issue(path, f"invalid maturity: {maturity}"))

        evidence = _as_list(metadata.get("emerged_from"))
        if "emerged_from" in metadata and not evidence:
            issues.append(_issue(path, "theme must record the evidence it emerged from"))
        elif maturity != "faded" and 0 < len(evidence) < MIN_THEME_EVIDENCE:
            issues.append(
                _warn(
                    path,
                    f"theme rests on fewer than {MIN_THEME_EVIDENCE} pieces of evidence",
                )
            )

        if not _is_configured_date(metadata.get("last_reviewed")):
            issues.append(_issue(path, "last_reviewed must be a configured YYYY-MM-DD date"))

        synthesized = metadata.get("last_synthesized")
        if "last_synthesized" in metadata:
            if not _is_configured_date(synthesized):
                issues.append(
                    _issue(path, "last_synthesized must be a configured YYYY-MM-DD date")
                )
            elif (today - date.fromisoformat(str(synthesized))).days > UNSYNTHESIZED_THEME_DAYS:
                issues.append(
                    _warn(
                        path,
                        f"theme has not been re-grounded in {UNSYNTHESIZED_THEME_DAYS} days",
                    )
                )

    return issues


def _validate_questions(wiki_root: Path, today: date) -> list[ValidationIssue]:
    """Open questions are the research agenda. They never fail a run, but a
    question nobody has resolved or dropped is a backlog item."""
    issues: list[ValidationIssue] = []
    seen: set[str] = set()

    for path in sorted((wiki_root / "questions").glob("*.md")):
        metadata = parse_frontmatter(path)
        for field in sorted(QUESTION_REQUIRED_FIELDS - metadata.keys()):
            issues.append(_issue(path, f"missing required field: {field}"))

        question_id = metadata.get("id")
        if not isinstance(question_id, str) or not question_id:
            issues.append(_issue(path, "id must be a non-empty string"))
            continue
        if question_id in seen:
            issues.append(_issue(path, f"duplicate question id: {question_id}"))
            continue
        seen.add(question_id)

        status = metadata.get("status")
        if "status" in metadata and status not in VALID_QUESTION_STATUSES:
            issues.append(_issue(path, f"invalid question status: {status}"))

        if status == "answered" and not _as_list(metadata.get("answered_by")):
            issues.append(_issue(path, "answered question must record answered_by"))

        try:
            raised = date.fromisoformat(str(metadata.get("raised")))
        except ValueError:
            issues.append(_issue(path, "raised must be YYYY-MM-DD"))
        else:
            if status == "open" and (today - raised).days > STALE_QUESTION_DAYS:
                issues.append(
                    _warn(
                        path,
                        f"question has been open for more than {STALE_QUESTION_DAYS} days; "
                        "answer or drop it",
                    )
                )

    return issues


def lint(root: Path, today: date) -> list[ValidationIssue]:
    root = root.resolve()
    wiki_root = root / "wiki"
    claim_paths = sorted((wiki_root / "claims").glob("*.md"))
    issues = _validate_setup(wiki_root)
    signal_issues, _ = _validate_signals(wiki_root, today)
    issues.extend(signal_issues)
    issues.extend(_validate_inbox(wiki_root, today))
    issues.extend(_validate_themes(wiki_root, today))
    issues.extend(_validate_questions(wiki_root, today))
    claims: dict[str, tuple[Path, dict[str, object]]] = {}

    for path in claim_paths:
        metadata = parse_frontmatter(path)
        claim_id = metadata.get("id")
        required_fields = REQUIRED_FIELDS | CURRENT_EVIDENCE_FIELDS
        missing = sorted(required_fields - metadata.keys())
        for field in missing:
            issues.append(_issue(path, f"missing required field: {field}"))

        if not isinstance(claim_id, str) or not claim_id:
            issues.append(_issue(path, "id must be a non-empty string"))
            continue
        if claim_id in claims:
            issues.append(_issue(path, f"duplicate claim id: {claim_id}"))
            continue
        claims[claim_id] = (path, metadata)

        status = metadata.get("status")
        if status not in VALID_STATUSES:
            issues.append(_issue(path, f"invalid status: {status}"))

        source_title = metadata.get("source_title")
        if "source_title" in metadata and (
            not isinstance(source_title, str) or not source_title.strip()
        ):
            issues.append(_issue(path, "source_title must be non-empty"))

        source_type = metadata.get("source_type")
        if "source_type" in metadata and source_type not in VALID_SOURCE_TYPES:
            issues.append(_issue(path, "source_type must be Confluence or Jira"))

        source_url = metadata.get("source_url")
        if not isinstance(source_url, str) or not source_url.startswith("https://"):
            issues.append(_issue(path, "source_url must begin with https://"))

        source_updated = metadata.get("source_updated")
        try:
            source_date = date.fromisoformat(str(source_updated))
        except ValueError:
            issues.append(_issue(path, "source_updated must be YYYY-MM-DD"))
        else:
            expected_freshness = _expected_freshness(source_date, today)
            freshness = metadata.get("freshness")
            if "freshness" in metadata and freshness != expected_freshness:
                issues.append(
                    _issue(
                        path,
                        f"freshness must be {expected_freshness} for source_updated",
                    )
                )
            if status in CUSTOMER_RELEVANT_STATUSES and (today - source_date).days > 90:
                issues.append(
                    _issue(
                        path,
                        "customer-relevant claim source_updated is older than 90 days",
                    )
                )

        effective_date = metadata.get("effective_date")
        if effective_date:
            try:
                target_date = date.fromisoformat(str(effective_date))
            except ValueError:
                issues.append(_issue(path, "effective_date must be YYYY-MM-DD"))
            else:
                if status == "current" and target_date < today:
                    issues.append(_issue(path, "current claim has past effective_date"))

    for claim_id, (path, metadata) in claims.items():
        for successor in _as_list(metadata.get("superseded_by")):
            successor_record = claims.get(successor)
            if not successor_record or claim_id not in _as_list(successor_record[1].get("supersedes")):
                issues.append(_issue(path, f"missing reciprocal supersession for {successor}"))
        for predecessor in _as_list(metadata.get("supersedes")):
            predecessor_record = claims.get(predecessor)
            if not predecessor_record or claim_id not in _as_list(predecessor_record[1].get("superseded_by")):
                issues.append(_issue(path, f"missing reciprocal supersession for {predecessor}"))

    # A claim is anchored only by the navigable wiki: product and theme pages,
    # the index, logs. Signals and inbox proposals are a staging area, so a
    # link from one of them does not rescue a claim from being an orphan.
    staging_dirs = {
        wiki_root / "claims",
        wiki_root / "signals",
        wiki_root / "inbox",
        wiki_root / "questions",
    }
    inbound_claim_links: set[Path] = set()
    for page in wiki_root.rglob("*.md"):
        for target in _wikilinks(page):
            if target.startswith("raw/"):
                continue
            target_path = wiki_root / f"{target}.md"
            if not target_path.exists():
                issues.append(_issue(page, f"missing wikilink target: {target}"))
            elif page.parent not in staging_dirs and target_path.parent == wiki_root / "claims":
                inbound_claim_links.add(target_path.resolve())

    for path in claim_paths:
        if path.resolve() not in inbound_claim_links:
            issues.append(_issue(path, "orphan claim has no inbound wikilink outside wiki/claims"))

    return sorted(issues, key=lambda issue: (str(issue.path), issue.message))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--today", type=date.fromisoformat, default=date.today())
    args = parser.parse_args()
    issues = lint(args.root, args.today)
    root = args.root.resolve()
    errors = [issue for issue in issues if issue.severity == "error"]
    warnings = [issue for issue in issues if issue.severity == "warning"]

    for issue in issues:
        location = issue.path.resolve().relative_to(root)
        print(f"{issue.severity}: {location}: {issue.message}")

    if errors:
        return 1
    if warnings:
        print(f"lint passed with {len(warnings)} warning(s)")
    else:
        print("lint passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
