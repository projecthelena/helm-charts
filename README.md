# ClusterCost Helm Charts

This repository hosts Helm charts for deploying the ClusterCost ecosystem. It currently includes:

- `charts/clustercost-dashboard`: renders the web dashboard that aggregates agent data.
- `charts/clustercost-agent-k8s`: publishes metrics from Kubernetes clusters to the dashboard.

## Getting Started

1. Inspect chart values to understand defaults:
   ```sh
   helm show values charts/clustercost-dashboard
   ```
2. Validate templates locally:
   ```sh
   helm lint charts/clustercost-dashboard
   helm template charts/clustercost-dashboard
   ```
3. Install into a test namespace:
   ```sh
   helm install dashboard charts/clustercost-dashboard --namespace clustercost --create-namespace
   ```

Refer to `AGENTS.md` for contribution guidelines, release expectations, and security notes.
