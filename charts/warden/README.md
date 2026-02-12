# Warden Chart

Helm chart for deploying the Warden policy engine as part of the Project Helena ecosystem.

## Installation

```sh
helm install warden charts/warden --namespace warden --create-namespace
```

Use `-f my-values.yaml` or `--set key=value` to override defaults.

## Database Modes

### SQLite (default)

Uses a PersistentVolumeClaim for storage. Replicas are forced to 1.

```yaml
database:
  type: sqlite
  sqlite:
    path: /data/warden.db
    persistence:
      enabled: true
      size: 1Gi
```

### Internal PostgreSQL (subchart)

Deploys a Bitnami PostgreSQL pod alongside Warden. Requires `helm dependency update` first.

```sh
helm dependency update charts/warden
```

```yaml
database:
  type: postgres
  postgres:
    enabled: true
postgresql:
  auth:
    username: warden
    password: "my-secret-password"
    database: warden
```

### External PostgreSQL

Point Warden at an existing PostgreSQL instance.

```yaml
database:
  type: postgres
  external:
    enabled: true
    url: "postgres://warden:password@db.example.com:5432/warden?sslmode=disable"
```

Or reference an existing Kubernetes secret:

```yaml
database:
  type: postgres
  external:
    enabled: true
    existingSecret: my-pg-secret
    existingSecretKey: db-url
```

## Key Values

| Value | Description | Default |
| --- | --- | --- |
| `replicaCount` | Number of warden pods (ignored for SQLite) | `1` |
| `image.repository` / `image.tag` | Container image reference | `ghcr.io/projecthelena/warden:latest` |
| `service.type` | Kubernetes Service type | `ClusterIP` |
| `service.port` | Service port | `9090` |
| `config.listenAddr` | App bind address | `":9090"` |
| `config.cookieSecure` | Set `true` for HTTPS deployments | `false` |
| `config.trustProxy` | Set `true` behind a reverse proxy | `false` |
| `database.type` | Database backend: `sqlite` or `postgres` | `sqlite` |
| `adminSecret` | Initial setup secret (avoid in production) | `""` |
| `ingress.enabled` | Enable Ingress resource | `false` |
| `commonLabels` | Extra labels applied to all resources | `{}` |
| `env` | Additional environment variables | `{}` |
| `resources` | Pod resource requests/limits | See `values.yaml` |

See `values.yaml` for the full list.

## Validation

Run the following before opening a PR:

```sh
helm lint charts/warden
helm template charts/warden | kubectl apply --dry-run=client -f -
```
