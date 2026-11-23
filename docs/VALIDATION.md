# Validation scope

Repository checks cover a strict package file allowlist, UTF-8/JSON parsing, local Markdown links and fragments, text-only/non-executable package rules, author/license markers, version notices and exact content hashes. Unit tests exercise release identity, generated-card handling and failure cases with synthetic fixtures.

These checks are deterministic packaging/release-engineering checks. They do not establish model behavior, legal accuracy, carbon-data assurance, runtime injection enforcement, professional certification or real customer outcomes. Existing bounded AI-branch model trials remain PARTIAL. No new model or real-world scenario tests are implied by adding CI or GitHub.

GitHub Actions runs only repository checks with read-only contents permission. The workflow has no registry secret and no publication step. A configured workflow is not evidence of a successful hosted run; inspect its actual run result.

The bundle has no third-party runtime dependencies. Maintainer tools use Python's standard library and the separately installed ClawHub CLI for read-only registry inspection. The repository retains the existing MIT-0 license. Scanner results are recorded separately and are never called a universal security certificate.
