# Carbon Accounting Review

A portable, evidence-led Agent Skill for reviewing GHG inventories, carbon disclosures and product-footprint methods.

**Author:** Simon Huang · **License:** [MIT-0](LICENSE) · **First release:** 2026-11-12

[ClawHub release](https://clawhub.ai/simon5530/skills/carbon-accounting-review) · [Skill instructions](skill/carbon-accounting-review/SKILL.md) · [Examples](skill/carbon-accounting-review/examples/README.md) · [Release workflow](docs/RELEASING.md)

## Source of truth

Local Git is the development source of truth. GitHub mirrors reviewed commits; ClawHub distributes explicitly published versions. There is no scheduled publishing, post-commit hook, automatic registry release or bidirectional overwrite.

| Location | Meaning |
|---|---|
| Local Git / GitHub main | Current development, possibly containing changes labelled Unreleased |
| Git tag v1.1.0 | Reconstructed source snapshot verified against the already published ClawHub 1.1.0; not its original publishing commit |
| ClawHub 1.1.0 | Current published baseline, 18 maintained source files |

GitHub main and the latest registry release need not be identical between releases. At release time, compare the **same version, Git commit, file list and SHA-256 values**. Registry-generated skill-card.md is not maintained source.

## What the skill does

- Trace boundaries, source coverage, factors, units, GWP basis and calculation evidence.
- Separate location-based / market-based Scope 2 and arithmetic / contractual eligibility.
- Produce findings with source locators, missing evidence and professional-review limits.
- Optionally triage AI transparency questions by jurisdiction, role, use and date.

It is not a carbon calculator, emissions-factor database, audit opinion, legal opinion, certification or production-validated compliance classifier. Small synthetic examples are not accuracy benchmarks. Prior bounded model trials remain **PARTIAL**; this Git migration does not add behavioral validation.

## Use the skill

Read the [package README](skill/carbon-accounting-review/README.md) and [security policy](skill/carbon-accounting-review/SECURITY.md). Begin with synthetic examples, not confidential client files. Use your host's supported Agent Skill installation flow; capabilities and data-processing permissions remain the host's responsibility.

Only the directory **skill/carbon-accounting-review/** is the ClawHub package. Repository tools, CI, tests and release records are maintainer tooling, not executable content shipped in the skill.

## Maintain locally

Requires Git and Python 3.9+; the local checks use only Python's standard library. ClawHub CLI is needed only for registry verification / manual publication, and GitHub authentication for pushes.

    make check
    make test
    git add <reviewed-files>
    git commit -m "Describe the change"
    make sync

make sync validates and pushes an already committed, clean main branch. It does not commit, pull, force-push, publish to ClawHub or create a release. If the remote advanced, inspect and fast-forward normally; do not overwrite it.

## Publish a version deliberately

Follow [RELEASING.md](docs/RELEASING.md): update version and changelog, review/test, commit/tag, build an immutable 18-file package, publish manually on ClawHub, then verify registry bytes against that Git tag. New GitHub commits alone never publish a ClawHub version.

See [release baseline](release-manifests/1.1.0.json), [validation scope](docs/VALIDATION.md), and [repository security policy](SECURITY.md).

## 中文工作方式

平常只維護本地 Git，再以明確的 git push／make sync 同步 GitHub。ClawHub 是「版本發布端」，不是開發工作樹：未發布修改可先存在 GitHub main，不會自動變成 ClawHub 新版。下次發布時固定版本、commit、tag 與檔案雜湊，再從 ClawHub 核對同一份內容。不要使用 clawhub sync --all，也不要把私人工作區、研究資料或 review 紀錄整批上傳。
