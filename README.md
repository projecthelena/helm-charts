# Project Helena Helm Charts

Helm charts for deploying the [Project Helena](https://github.com/projecthelena) ecosystem — Kubernetes cost visibility and FinOps.

## Charts

| Chart | Description |
| --- | --- |
| [recon](charts/recon) | Web dashboard that aggregates cost metrics from distributed agents. Includes optional VictoriaMetrics for time-series storage. |
| [recon-agent](charts/recon-agent) | DaemonSet agent that collects cluster cost data via eBPF and reports to recon over gRPC. |
| [warden](charts/warden) | Policy engine for enforcing cost and operational policies. Supports SQLite and PostgreSQL backends. |

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
