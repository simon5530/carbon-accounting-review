# Security and disclosure boundaries

The distributed skill's [SECURITY.md](skill/carbon-accounting-review/SECURITY.md) governs its intended evidence and data-handling workflow. It does not enforce host permissions by itself.

This repository additionally contains maintainer-only Python tools. They read the declared package, Git blobs and public registry metadata; package creation writes only ignored dist outputs. No publishing token, API key, local account store or private memory belongs in Git.

Before the first push, a visibility change or release, scan the current tree and reachable history, inspect semantic privacy, review the exact diff, and verify licenses and source identity. A private repository does not make secret commits acceptable.

Do not include client data, personal records, credentials, licensed standards, source PDFs, real execution logs or screenshots in issues or pull requests. Report sensitive findings privately through GitHub's reporting channel if enabled; do not assume it is available or publish the material to demonstrate a bug.

The release helper never publishes, changes access controls, installs dependencies or disables TLS checks. Registry verification requires the maintained ClawHub CLI and uses its normal HTTPS behavior. An access failure is not a mismatch or a successful verification.
