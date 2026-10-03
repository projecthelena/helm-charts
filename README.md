# Project Helena Helm Charts

Helm charts for deploying the [Project Helena](https://github.com/projecthelena) ecosystem: uptime monitoring and Kubernetes cost visibility.

## Charts

| Chart | Description |
| --- | --- |
| [recon](charts/recon) | Web dashboard that aggregates cost metrics from distributed agents. Includes optional VictoriaMetrics for time-series storage. |
| [recon-agent](charts/recon-agent) | DaemonSet agent that collects cluster cost data via eBPF and reports to recon over gRPC. |
| [warden](charts/warden) | Uptime monitoring with adaptive latency alerts and status pages. Supports SQLite and PostgreSQL. |

## Usage

Add the Helm repository:

```sh
helm repo add projecthelena https://charts.projecthelena.com
helm repo update
```

Install a chart:

```sh
helm install recon projecthelena/recon --namespace recon --create-namespace
```

Or install directly from source:

```sh
helm install recon charts/recon --namespace recon --create-namespace
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
