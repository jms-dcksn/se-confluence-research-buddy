from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.lint_wiki import lint


VALID_CLAIM = """---
id: CLM-20260815-001
title: Example Product release is scheduled for 2026-09-15
products: [Example Product]
themes: [roadmap]
claim_type: release_target
status: current
effective_date: 2026-09-15
source_title: Example Product release plan
source_type: Confluence
source_updated: 2026-07-24
freshness: RECENT
source_url: https://example.test/product-release
evidence_note: The plan lists the Example Product release on 2026-09-15.
source_record: "[[raw/confluence/2026-07-24-daily-digest]]"
supersedes: []
superseded_by: []
confidence: high
---

## Evidence
"""


class LintWikiTests(unittest.TestCase):
    def write_claim(self, root: Path, name: str, content: str) -> None:
        path = root / "wiki" / "claims" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_page(self, root: Path, name: str, content: str) -> None:
        path = root / "wiki" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def write_setup_files(
        self,
        root: Path,
        *,
        index_date: str = "2026-07-27",
        topics: str = "  - Product Atlas\n  - Product Beacon",
        destination: str = r"C:\Research\product-wiki",
        timezone: str = "America/Chicago",
        digest_time: str = "09:00",
        configured_date: str = "2026-07-27",
    ) -> None:
        self.write_page(
            root,
            "index.md",
            f"""---
title: Confluence Research Wiki
kind: index
last_reviewed: {index_date}
---
""",
        )
        self.write_page(
            root,
            "research-scope.md",
            f"""---
title: Research Scope
kind: research-scope
topics:
{topics}
destination: {destination}
timezone: {timezone}
digest_time: "{digest_time}"
last_configured: {configured_date}
---
""",
        )

    def test_rejects_an_unconfigured_index(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_setup_files(root, index_date="YYYY-MM-DD")
            issues = lint(root, date(2026, 7, 27))
        self.assertTrue(
            any(
                issue.path.name == "index.md"
                and issue.message == "last_reviewed must be a configured YYYY-MM-DD date"
                for issue in issues
            )
        )

    def test_rejects_incomplete_research_scope(self) -> None:
        cases = (
            ({"topics": ""}, "topics must contain at least one configured topic"),
            ({"destination": "TO_BE_CONFIGURED"}, "destination must be configured"),
            ({"timezone": "TO_BE_CONFIGURED"}, "timezone must be configured"),
            ({"digest_time": "TO_BE_CONFIGURED"}, "digest_time must be configured"),
            (
                {"configured_date": "YYYY-MM-DD"},
                "last_configured must be a configured YYYY-MM-DD date",
            ),
        )
        for overrides, expected in cases:
            with self.subTest(expected=expected), TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_setup_files(root, **overrides)
                issues = lint(root, date(2026, 7, 27))
            self.assertTrue(any(issue.message == expected for issue in issues))

    def test_accepts_a_fully_configured_setup(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_setup_files(root)
            issues = lint(root, date(2026, 7, 27))
        self.assertEqual([], issues)

    def test_accepts_a_complete_current_claim(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claim(root, "product-release.md", VALID_CLAIM)
            self.write_page(root, "products/example-product.md", "[[claims/product-release]]")
            issues = lint(root, date(2026, 7, 24))
        self.assertEqual([], issues)

    def test_claim_template_satisfies_current_evidence_contract(self) -> None:
        template = (
            Path(__file__).resolve().parents[1] / "templates" / "claim.md"
        ).read_text(encoding="utf-8")
        claim = (
            template
            .replace("CLM-YYYYMMDD-NNN", "CLM-20260815-999")
            .replace("effective_date: YYYY-MM-DD", "effective_date: 2026-09-15")
            .replace("source_updated: YYYY-MM-DD", "source_updated: 2026-07-28")
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claim(root, "from-template.md", claim)
            self.write_page(root, "products/example-product.md", "[[claims/from-template]]")
            issues = lint(root, date(2026, 7, 28))
        self.assertEqual([], issues)

    def test_rejects_an_uncited_claim(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claim(
                root,
                "uncited.md",
                VALID_CLAIM.replace("source_url: https://example.test/product-release\n", ""),
            )
            issues = lint(root, date(2026, 7, 24))
        self.assertTrue(any("source_url" in issue.message for issue in issues))

    def test_rejects_a_stale_current_claim(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            claim = (
                VALID_CLAIM
                .replace("source_updated: 2026-07-24", "source_updated: 2026-04-01")
                .replace("freshness: RECENT", "freshness: STALE - VERIFY BEFORE CUSTOMER USE")
            )
            self.write_claim(
                root,
                "stale.md",
                claim,
            )
            issues = lint(root, date(2026, 7, 24))
        self.assertTrue(any("older than 90 days" in issue.message for issue in issues))

    def test_rejects_stale_customer_relevant_statuses(self) -> None:
        for status in ("current", "at-risk", "proposed"):
            with self.subTest(status=status), TemporaryDirectory() as directory:
                root = Path(directory)
                claim = (
                    VALID_CLAIM
                    .replace("status: current", f"status: {status}")
                    .replace("source_updated: 2026-07-24", "source_updated: 2026-03-01")
                    .replace("freshness: RECENT", "freshness: STALE - VERIFY BEFORE CUSTOMER USE")
                )
                self.write_claim(root, f"{status}.md", claim)
                issues = lint(root, date(2026, 7, 27))
            self.assertTrue(any("older than 90 days" in issue.message for issue in issues))

    def test_requires_evidence_contract_fields(self) -> None:
        field_lines = {
            "source_title": "source_title: Example Product release plan\n",
            "source_type": "source_type: Confluence\n",
            "freshness": "freshness: RECENT\n",
        }
        for field, line in field_lines.items():
            with self.subTest(field=field), TemporaryDirectory() as directory:
                root = Path(directory)
                self.write_claim(root, f"missing-{field}.md", VALID_CLAIM.replace(line, ""))
                issues = lint(root, date(2026, 7, 28))
            self.assertTrue(
                any(issue.message == f"missing required field: {field}" for issue in issues)
            )

    def test_rejects_invalid_source_type(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claim(
                root,
                "invalid-source-type.md",
                VALID_CLAIM.replace("source_type: Confluence", "source_type: Email"),
            )
            issues = lint(root, date(2026, 7, 28))
        self.assertTrue(any("source_type must be Confluence or Jira" in issue.message for issue in issues))

    def test_rejects_blank_source_title(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claim(
                root,
                "blank-source-title.md",
                VALID_CLAIM.replace(
                    "source_title: Example Product release plan",
                    "source_title:",
                ),
            )
            issues = lint(root, date(2026, 7, 28))
        self.assertTrue(any("source_title must be non-empty" in issue.message for issue in issues))

    def test_accepts_jira_as_a_source_type(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            claim = (
                VALID_CLAIM
                .replace("source_type: Confluence", "source_type: Jira")
                .replace(
                    "source_url: https://example.test/product-release",
                    "source_url: https://jira.example.test/browse/EXAMPLE-1",
                )
            )
            self.write_claim(root, "jira-source.md", claim)
            self.write_page(root, "products/example-product.md", "[[claims/jira-source]]")
            issues = lint(root, date(2026, 7, 28))
        self.assertEqual([], issues)

    def test_rejects_date_inconsistent_freshness(self) -> None:
        cases = (
            ("2026-07-24", "CURRENT WINDOW", "RECENT"),
            ("2026-06-01", "RECENT", "CURRENT WINDOW"),
            ("2026-03-01", "CURRENT WINDOW", "STALE - VERIFY BEFORE CUSTOMER USE"),
        )
        for source_updated, freshness, expected in cases:
            with self.subTest(source_updated=source_updated), TemporaryDirectory() as directory:
                root = Path(directory)
                claim = (
                    VALID_CLAIM
                    .replace("status: current", "status: superseded")
                    .replace("source_updated: 2026-07-24", f"source_updated: {source_updated}")
                    .replace("freshness: RECENT", f"freshness: {freshness}")
                )
                self.write_claim(root, "wrong-freshness.md", claim)
                issues = lint(root, date(2026, 7, 27))
            self.assertTrue(
                any(issue.message == f"freshness must be {expected} for source_updated" for issue in issues)
            )

    def test_does_not_allow_legacy_evidence_exceptions(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            legacy_claim = (
                VALID_CLAIM
                .replace("CLM-20260815-001", "CLM-20260115-001")
                .replace("source_title: Example Product release plan\n", "")
                .replace("source_type: Confluence\n", "")
                .replace("freshness: RECENT\n", "")
            )
            self.write_claim(root, "legacy.md", legacy_claim)
            self.write_page(root, "products/example-product.md", "[[claims/legacy]]")
            issues_without_exception = lint(root, date(2026, 7, 28))
            exception_path = root / "wiki" / "evidence-contract-legacy-claims.txt"
            exception_path.write_text("CLM-20260115-001\n", encoding="utf-8")
            issues_with_exception = lint(root, date(2026, 7, 28))
        for issues in (issues_without_exception, issues_with_exception):
            self.assertTrue(
                any(
                    issue.message == "missing required field: source_title"
                    for issue in issues
                )
            )

    def test_rejects_a_non_string_claim_id_without_crashing(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            claim = VALID_CLAIM.replace(
                "id: CLM-20260815-001",
                "id: [CLM-20260815-001]",
            )
            self.write_claim(root, "invalid-id.md", claim)
            issues = lint(root, date(2026, 7, 28))
        self.assertTrue(
            any(issue.message == "id must be a non-empty string" for issue in issues)
        )

    def test_uses_status_neutral_stale_diagnostic(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            claim = (
                VALID_CLAIM
                .replace("status: current", "status: at-risk")
                .replace("source_updated: 2026-07-24", "source_updated: 2026-03-01")
                .replace("freshness: RECENT", "freshness: STALE - VERIFY BEFORE CUSTOMER USE")
            )
            self.write_claim(root, "at-risk.md", claim)
            issues = lint(root, date(2026, 7, 27))
        self.assertTrue(
            any(
                issue.message == "customer-relevant claim source_updated is older than 90 days"
                for issue in issues
            )
        )

    def test_requires_reciprocal_supersession(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            old_claim = (
                VALID_CLAIM.replace("CLM-20260815-001", "CLM-20260801-001")
                .replace("status: current", "status: superseded")
                .replace("superseded_by: []", "superseded_by: [CLM-20260815-001]")
            )
            self.write_claim(root, "old.md", old_claim)
            self.write_claim(root, "new.md", VALID_CLAIM)
            issues = lint(root, date(2026, 7, 24))
        self.assertTrue(any("reciprocal" in issue.message for issue in issues))

    def test_accepts_reciprocal_supersession(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            old_claim = (
                VALID_CLAIM.replace("CLM-20260815-001", "CLM-20260801-001")
                .replace("status: current", "status: superseded")
                .replace("effective_date: 2026-09-15", "effective_date: 2026-09-08")
                .replace("superseded_by: []", "superseded_by: [CLM-20260816-001]")
            )
            new_claim = (
                VALID_CLAIM.replace("CLM-20260815-001", "CLM-20260816-001")
                .replace("effective_date: 2026-09-15", "effective_date: 2026-09-22")
                .replace("supersedes: []", "supersedes: [CLM-20260801-001]")
            )
            self.write_claim(root, "old-product-release.md", old_claim)
            self.write_claim(root, "revised-product-release.md", new_claim)
            self.write_page(
                root,
                "products/example-product.md",
                "[[claims/old-product-release]]\n[[claims/revised-product-release]]",
            )
            issues = lint(root, date(2026, 7, 25))
        self.assertEqual([], issues)

    def test_rejects_a_past_due_current_target(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claim(
                root,
                "past-due.md",
                VALID_CLAIM.replace("effective_date: 2026-09-15", "effective_date: 2026-07-01"),
            )
            issues = lint(root, date(2026, 7, 24))
        self.assertTrue(any("past effective_date" in issue.message for issue in issues))

    def test_rejects_missing_wikilink_target(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claim(root, "product-release.md", VALID_CLAIM)
            self.write_page(root, "products/example-product.md", "[[claims/missing-claim]]")
            issues = lint(root, date(2026, 7, 24))
        self.assertTrue(any("missing wikilink target" in issue.message for issue in issues))

    def test_rejects_an_orphan_claim(self) -> None:
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_claim(root, "orphan.md", VALID_CLAIM)
            issues = lint(root, date(2026, 7, 24))
        self.assertTrue(any("orphan claim" in issue.message for issue in issues))


if __name__ == "__main__":
    unittest.main()
