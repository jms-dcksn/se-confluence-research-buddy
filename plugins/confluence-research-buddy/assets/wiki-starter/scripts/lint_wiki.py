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


@dataclass(frozen=True)
class ValidationIssue:
    path: Path
    message: str


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


def _issue(path: Path, message: str) -> ValidationIssue:
    return ValidationIssue(path=path, message=message)


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
        topics = _as_list(scope.get("topics"))
        if not topics or any(not _is_configured_text(topic) for topic in topics):
            issues.append(
                _issue(
                    scope_path,
                    "topics must contain at least one configured topic",
                )
            )
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


def lint(root: Path, today: date) -> list[ValidationIssue]:
    root = root.resolve()
    wiki_root = root / "wiki"
    claim_paths = sorted((wiki_root / "claims").glob("*.md"))
    issues = _validate_setup(wiki_root)
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

    inbound_claim_links: set[Path] = set()
    for page in wiki_root.rglob("*.md"):
        for target in _wikilinks(page):
            if target.startswith("raw/"):
                continue
            target_path = wiki_root / f"{target}.md"
            if not target_path.exists():
                issues.append(_issue(page, f"missing wikilink target: {target}"))
            elif page.parent != wiki_root / "claims" and target_path.parent == wiki_root / "claims":
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
    if issues:
        root = args.root.resolve()
        for issue in issues:
            print(f"{issue.path.resolve().relative_to(root)}: {issue.message}")
        return 1
    print("lint passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
