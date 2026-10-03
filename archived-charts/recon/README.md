# Recon Dashboard Chart

Helm chart for deploying the Recon dashboard component. It renders a web UI that aggregates metrics from deployed Recon agents.

## Installation

```sh
helm install recon charts/recon --namespace recon --create-namespace
```

Use `-f my-values.yaml` or `--set key=value` to override defaults.

## Key Values

| Value | Description | Default |
| --- | --- | --- |
| `replicaCount` | Number of dashboard pods | `1` |
| `image.repository` / `image.tag` | Container image reference | `ghcr.io/projecthelena/recon:latest` |
| `service.type` | Kubernetes Service type | `ClusterIP` |
| `commonLabels` | Extra labels applied to all dashboard resources | `{}` |
| `agents` | Optional list of agent endpoints; overrides `config.agents` | `[]` |
| `config` | Dashboard YAML config rendered into a ConfigMap | See `values.yaml` |
| `env` | Extra environment variables for the container | DISABLE_HTTP_POLLING, VICTORIA_METRICS_URL |
| `victoriaMetrics.enabled` | Deploy a single-node VictoriaMetrics instance | `true` |
| `victoriaMetrics.persistence` | VictoriaMetrics PVC settings | See `values.yaml` |
| `ingress.enabled` | Creates an Ingress pointing to the dashboard service | `false` |

See `values.yaml` for the full list.

## Features

- Built-in config checksum annotations trigger rollouts when `config` changes.
- Readiness/liveness probes are enabled by default; override probe paths or timings via `values.yaml`.
- Optional Ingress manifests render when `ingress.enabled` is true for exposing the dashboard externally.
- `values.schema.json` provides validation and IDE hints when overriding values.

## Validation

Run the following before opening a PR:

```sh
helm lint charts/recon
helm template charts/recon | kubectl apply --dry-run=client -f -
```

## Related Docs

- Contribution and testing guidelines: `AGENTS.md`
- Repository overview: root `README.md`
