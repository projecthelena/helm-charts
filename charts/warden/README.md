# Warden Chart

Deploy Warden on Kubernetes to monitor HTTP, TCP, ICMP, and DNS services with adaptive latency alerts and status pages. Use SQLite or PostgreSQL for storage.

Run one Warden replica with either database. Each process schedules its own checks, so PostgreSQL does not enable active-active operation. Upgrades use `Recreate` to avoid overlapping schedulers and briefly interrupt checks.

Warden is built by [Project Helena](https://projecthelena.com/). Visit the website for a product overview and updates.

## Installation

```sh
helm repo add projecthelena https://charts.projecthelena.com
helm repo update
helm install warden projecthelena/warden --namespace warden --create-namespace
```

Use `-f my-values.yaml` or `--set key=value` to override defaults. The default image is pinned to a stable Warden release.

For reproducible installs, choose a chart version with `helm search repo projecthelena/warden --versions` and pass `--version <chart-version>` to `helm install` or `helm upgrade`. The chart version and Warden application version are independent.

After installation, run `kubectl port-forward --namespace warden service/warden 9090:9090` and open `http://localhost:9090` to create the first administrator. For an HTTPS ingress, set `config.cookieSecure=true`; enable `config.trustProxy` only behind a trusted proxy.

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

Deploys a PostgreSQL StatefulSet alongside Warden using the official `postgres:18` image. Enable either internal or external PostgreSQL, never both.

```yaml
database:
  type: postgres
  postgres:
    enabled: true
    auth:
      username: warden
      password: "my-secret-password"  # auto-generated if omitted
      database: warden
    persistence:
      enabled: true
      size: 5Gi
```

Or reference an existing Kubernetes secret (must contain `password` and `db-url` keys):

```yaml
database:
  type: postgres
  postgres:
    enabled: true
    auth:
      existingSecret: my-pg-credentials
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

## ArgoCD

When using the internal PostgreSQL with an auto-generated password, ArgoCD will
regenerate a new random password on every sync because the Helm `lookup`
function is disabled in ArgoCD's repo-server. To prevent this, configure your
ArgoCD Application to ignore differences on the PostgreSQL secret:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
spec:
  # ... your existing spec ...
  ignoreDifferences:
    - kind: Secret
      name: <release>-warden-postgresql
      jsonPointers:
        - /data
  syncPolicy:
    syncOptions:
      - RespectIgnoreDifferences=true
```

Replace `<release>` with your Helm release name. This ensures the password
created on first sync is preserved on all subsequent syncs.

Alternatively, set an explicit password or use an externally managed secret to
avoid the issue entirely:

```yaml
database:
  postgres:
    auth:
      password: "my-stable-password"
      # -- or --
      existingSecret: my-pg-credentials
```

## Key Values

| Value | Description | Default |
| --- | --- | --- |
| `replicaCount` | Warden replicas (must remain 1) | `1` |
| `image.repository` / `image.tag` | Container image reference | See `image` in `values.yaml` for the pinned release |
| `service.type` | Kubernetes Service type | `ClusterIP` |
| `service.port` | Service port; routes to the port in `config.listenAddr` | `9090` |
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

## Observability

Enable `observability.enabled` for the private Prometheus and profiling listener. Its port must differ from the HTTP listener, and the service must use `ClusterIP`. Do not expose this port through an ingress or external load balancer.
