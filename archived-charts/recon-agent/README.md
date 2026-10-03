# Recon Agent Helm Chart

This chart deploys the Recon Kubernetes cost agent as a cluster-wide DaemonSet with optional eBPF and remote reporting support.

## Installation

```bash
helm repo add projecthelena https://charts.projecthelena.com
helm repo update
helm install recon-agent projecthelena/recon-agent \
  --namespace recon-agent --create-namespace
```

For local changes, run from the repo root:

```bash
helm install recon-agent ./deployment/helm \
  --namespace recon-agent --create-namespace
```

## Configuration

The agent is primarily configured via environment variables.

| Value | Description | Default |
| :--- | :--- | :--- |
| `image.repository` | Container image | `ghcr.io/projecthelena/recon-agent` |
| `image.tag` | Image tag. Defaults to chart appVersion when empty | `""` |
| `clusterName` | Optional cluster name. If set, injects `CLUSTER_NAME` env var. | `""` |
| `env` | List of environment variables for agent configuration | see `values.yaml` |
| `resources` | Pod resource requests/limits | see `values.yaml` |
| `nodeSelector` / `tolerations` | Scheduling settings | `{}` |
| `service.port` | Service port | `8080` |
| `service.type` | Service type | `ClusterIP` |

### Environment Variables

Configure the agent behavior by adding items to the `env` list in `values.yaml`:

```yaml
env:
  - name: RECON_ENABLE_NETWORK
    value: "true"
  - name: RECON_SCRAPE_INTERVAL
    value: "15"
  - name: RECON_REMOTE_ENDPOINT
    value: "dashboard.example.com:9091"
  - name: RECON_REMOTE_AUTH_TOKEN
    value: "my-token"
```

For full list of supported environment variables, refer to the [Agent Documentation](https://docs.projecthelena.com).
