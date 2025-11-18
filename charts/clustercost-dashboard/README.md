# Clustercost Dashboard Chart

Helm chart for deploying the ClusterCost dashboard component. It renders a web UI that aggregates metrics from deployed ClusterCost agents.

## Installation

```sh
helm install clustercost-dashboard charts/clustercost-dashboard --namespace clustercost --create-namespace
```

Use `-f my-values.yaml` or `--set key=value` to override defaults.

## Key Values

| Value | Description | Default |
| --- | --- | --- |
| `replicaCount` | Number of dashboard pods | `1` |
| `image.repository` / `image.tag` | Container image reference | `ghcr.io/clustercost/dashboard:latest` |
| `service.type` | Kubernetes Service type | `ClusterIP` |
| `config` | Dashboard YAML config rendered into a ConfigMap | See `values.yaml` |
| `env` | Extra environment variables for the container | LISTEN_ADDR / CONFIG_FILE |

See `values.yaml` for the full list.

## Validation

Run the following before opening a PR:

```sh
helm lint charts/clustercost-dashboard
helm template charts/clustercost-dashboard | kubectl apply --dry-run=client -f -
```

## Related Docs

- Contribution and testing guidelines: `AGENTS.md`
- Repository overview: root `README.md`
