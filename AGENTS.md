# Repository Guidelines

## Project Structure & Module Organization
- `charts/` contains all Helm packages; each chart lives in its own directory (e.g., `charts/recon`, `charts/recon-agent`, `charts/warden`).
- Each chart follows the Helm layout: `Chart.yaml`, `values.yaml`, and `templates/` with Kubernetes manifests (Deployment, Service, ConfigMap, etc.).
- Keep chart-specific assets (helpers, notes) inside their chart directory; avoid cross-chart imports.

## Build, Test, and Development Commands
- `helm lint charts/<chart-name>`: static validation for a chart; run before every PR.
- `helm template charts/<chart-name>`: render manifests locally for inspection, e.g., `helm template charts/recon`.
- `helm install <release> charts/<chart-name> --namespace <ns>`: deploy to a cluster; use a sandbox namespace when testing new changes.

## Coding Style & Naming Conventions
- YAML files use two-space indentation and lowercase keys.
- Follow Helm best practices: keep helper templates in `_helpers.tpl`, parameterize user-facing values, and avoid hardcoding namespaces.
- When adding values, provide sane defaults in `values.yaml` and document them via inline comments where needed.

## Testing Guidelines
- Prefer `helm lint` and `helm template` for validation; add automated tests (e.g., `ct lint`) when the repo grows.
- Rendered manifests should be Kubernetes-valid; use `kubectl apply --dry-run=client -f <(helm template …)` as an optional smoke test.
- Test files should mirror chart names; add sample overrides under `charts/<chart>/ci/` if you introduce scenario-specific testing.

## Commit & Pull Request Guidelines
- Commit messages follow the conventional short imperative style (e.g., `feat: add dashboard values`).
- Each PR should summarize the change set, link related issues, and note validation results (helm lint/template, deployment notes).
- Include screenshots or logs when altering user-visible behavior (e.g., dashboard config changes) so reviewers can verify outcomes quickly.

## Security & Configuration Tips
- Never commit secrets; leverage Kubernetes Secrets and reference them via `values.yaml`.
- Default images should point to trusted registries (`ghcr.io/projecthelena/...`). Bump tags intentionally and document breaking changes.
- Provide configuration examples for connecting agents (e.g., `values.yaml` `config.agents`) so operators can mirror recommended settings.

## Publishing and Artifact Hub

- Build validation runs on pull requests; only pushes to `main` deploy to Cloudflare Pages. The full workflow is serialized per ref so concurrent builds do not replace a newer deployment with an older one.
- Keep Helm pinned to the same version as the Warden release workflow. Run `python3 .github/scripts/test_package_charts.py`, `helm lint`, `helm template`, and `actionlint` when changing publishing.
- `.github/scripts/package_charts.py` requires an empty `dist/` and access to the existing public repository. It preserves old packages, including prereleases, and rejects changes to published versions. Repository download failures must stop publication, never reset history.
- Register `https://charts.projecthelena.com` once in Artifact Hub. Add its real repository UUID as `repositoryID` in `artifacthub-repo.yml` after registration; never invent an ID. Set the owner email to the address used by the publisher account if ownership claiming is needed.
- `artifacthub-repo.yml` is copied beside `index.yaml`. Verified publisher status requires a real ID and a subsequent index change. This preparation alone does not register or verify the repository.
- Chart automation from Warden needs the write-enabled deploy key configured by its PR #103. Merge the chart publication changes before enabling stable-release synchronization. Registration, credential creation, and merges remain separate operations.
