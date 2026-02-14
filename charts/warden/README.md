# Warden Chart

Helm chart for deploying Warden — open-source uptime monitoring built in Go. Multi-zone checks, status pages, unlimited team members. Part of the Project Helena ecosystem.

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

### Internal PostgreSQL

Deploys a PostgreSQL StatefulSet alongside Warden using the official `postgres:18` image.

```yaml
database:
  type: postgres
  postgres:
    enabled: true
    auth:
      username: warden
      password: "my-secret-password"   # auto-generated if omitted
      database: warden
    persistence:
      enabled: true
      size: 5Gi
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

## Exposing Warden

The chart supports two ways to expose Warden externally: standard Kubernetes Ingress and Traefik IngressRoute. You can enable one or both depending on your setup.

### Kubernetes Ingress

Works with any ingress controller (nginx, HAProxy, etc.). The chart auto-detects the cluster API version and renders the correct format (`networking.k8s.io/v1`, `networking.k8s.io/v1beta1`, or `extensions/v1beta1`).

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
  hosts:
    - host: status.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: status-tls
      hosts:
        - status.example.com
```

### Traefik IngressRoute

Native Traefik CRD (`traefik.io/v1alpha1`). Use this when running Traefik as your ingress controller and you want access to Traefik-specific features like middlewares and cert resolvers.

```yaml
ingressRoute:
  enabled: true
  entryPoints:
    - websecure
  routes:
    - match: Host(`status.example.com`)
      kind: Rule
  tls:
    certResolver: letsencrypt
```

Routes default to the warden service and port. To override, specify `services` explicitly:

```yaml
ingressRoute:
  enabled: true
  entryPoints:
    - websecure
  routes:
    - match: Host(`status.example.com`)
      kind: Rule
      services:
        - name: my-custom-service
          port: 8080
      middlewares:
        - name: my-middleware
  tls:
    certResolver: letsencrypt
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
| `ingress.enabled` | Enable Kubernetes Ingress resource | `false` |
| `ingressRoute.enabled` | Enable Traefik IngressRoute resource | `false` |
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
