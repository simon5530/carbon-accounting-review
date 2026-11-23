# Local Git → GitHub → explicit ClawHub release

## Everyday development

Edit only the maintained package under skill/carbon-accounting-review/ and deliberate repository support files. Run make check and make test, review git diff, commit, then make sync. This pushes a clean main branch; no hook or scheduler publishes anything.

Keep Unreleased changes clearly marked. Do not represent GitHub main as the already published package while it differs from the last release. Do not copy private review evidence, model transcripts, standards text or local configuration into this repository.

## Version release checklist

1. Choose a new semantic version. Update SKILL.md, package README/GOVERNANCE version metadata where applicable, version date and CHANGELOG. Remove the working-copy Unreleased notice only for the content actually being released. Do not relabel old behavioral trials as new validation.
2. Run make check and make test; inspect the entire diff and exact package allowlist in skill-files.json. Run a maintained secret scanner on the tree and reachable Git history, and separately review semantic privacy. Do not ship unresolved findings.
3. Commit the reviewed source, create an annotated vX.Y.Z tag, and explicitly push the source and tag to the intended GitHub repository after publication approval where required. No force-push.
4. Build from that immutable tag:

       python3 tools/release.py pack X.Y.Z --ref vX.Y.Z

   This creates dist/carbon-accounting-review-X.Y.Z/ and a ZIP containing only the declared package files, plus a separate source manifest. No repository scripts, private review evidence or generated registry card enters the upload.
5. Publish yourself on ClawHub using that staged directory/ZIP. For CLI publication, first check clawhub whoami and the intended owner. The installed CLI supports:

       clawhub skill publish ./dist/carbon-accounting-review-X.Y.Z \
         --owner simon5530 --slug carbon-accounting-review --version X.Y.Z \
         --source-repo simon5530/carbon-accounting-review \
         --source-commit REVIEWED_FULL_COMMIT_SHA --source-ref vX.Y.Z \
         --source-path skill/carbon-accounting-review --dry-run --json

   Inspect the dry-run file list and digest. Only when deliberately publishing the approved exact payload, repeat without --dry-run and include the final changelog. Source metadata must refer to that same reviewed commit; it is not proof that the registry accepted or published it. A private GitHub repository is not anonymous source availability.
6. Upload accepted, pending checks and publicly available are separate states. After publication, verify rather than blindly retry:

       python3 tools/release.py verify X.Y.Z --ref vX.Y.Z
       python3 tools/release.py record X.Y.Z --ref vX.Y.Z

   record writes a release-manifests entry only after successful owner/version/file/hash verification and never overwrites a conflicting record. Review/commit/push that receipt separately; the release tag continues to identify the source commit, not the later receipt commit.

## Existing 1.1.0

v1.1.0 reconstructs the 18 source files already published on 2026-11-22 and verified on 2026-11-23. It is not a claim that the original publication used this newly created Git history. Do not republish 1.1.0.

    python3 tools/release.py verify 1.1.0 --ref v1.1.0

The registry-generated skill-card.md is recorded separately, not maintained or uploaded. Any other unexpected registry file, missing file or hash mismatch fails verification. Head changes remain Unreleased until the next explicit publication. Never run clawhub sync --all for this project.

## Recovery

If a request times out after submission, inspect the existing version and content identity before any retry. Keep accepted observations, unknown state and missing coverage explicit. If registry content differs, compare it on a separate branch or snapshot; never overwrite uncommitted local work automatically. TLS/auth/quota failures are blockers, not reasons to disable checks or repeatedly publish.
