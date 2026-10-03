# Project Helena Helm Charts

Helm charts for deploying the [Project Helena](https://projecthelena.com/) uptime monitoring service.

## Charts

| Chart | Description |
| --- | --- |
| [warden](charts/warden) | Uptime monitoring with adaptive latency alerts and status pages. Supports SQLite and PostgreSQL. |

## Usage

Add the Helm repository:

```sh
helm repo add projecthelena https://charts.projecthelena.com
helm repo update
```

Install a chart:

```sh
helm install warden projecthelena/warden --namespace warden --create-namespace
```

Or install directly from source:

```sh
helm install warden charts/warden --namespace warden --create-namespace
```

## Development

```sh
# Lint a chart
helm lint charts/<chart-name>

# Render templates locally
helm template charts/<chart-name>

# For charts with dependencies (e.g. warden with PostgreSQL)
helm dependency update charts/<chart-name>
```

Refer to `AGENTS.md` for contribution guidelines and security notes.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.

## Chart releases

Chart versions follow semantic versioning independently from application versions. Stable Warden releases update its chart after container images are published. Release candidates do not change the chart defaults.

Each deployment keeps the existing chart packages and adds new versions to `index.yaml`. Publishing different contents under an existing chart version fails; increment `version` in `Chart.yaml` when changing a chart. Previously discarded versions cannot be recovered by this pipeline.

Artifact Hub indexes new packages automatically once `https://charts.projecthelena.com` is registered as a Helm repository. It reads the chart description and README from each package.

## Retired packages

Recon and Recon Agent are disabled because their images are unavailable. Their sources live in `archived-charts/` and are excluded from builds. `retired-packages.json` lists archives kept at their original download URLs but excluded from `index.yaml`, including Warden 0.3.0 with its broken logo metadata. Subsequent builds fetch these archives explicitly so retirement never deletes historical downloads. Use Warden 0.3.1 or newer.

The deployed root `404.html` disables Cloudflare Pages SPA fallback: missing files, including optional `.prov` signatures, must return HTTP 404 rather than the landing page with HTTP 200.
