# ERPNext Service Role

This repository packages the ERPNext application runtime as a service
contract that integrates with the Shared Services infrastructure framework.
The role consumes dependency exports for MariaDB and Redis peers and
produces a runtime definition that can be rendered or applied by the
framework-provided `common.render_runtime` and `common.apply_runtime` roles.

## Dependency contracts

The service expects dependency exports that follow the framework registry
schema:

- **Database** (`database` export)
  - `env`: `DATABASE_HOST`, `DATABASE_PORT`, `DATABASE_NAME`,
    `DATABASE_USER`, `MARIADB_VERSION`, `DB_SSL_MODE`
  - `secrets`: `DATABASE_PASSWORD`
- **Cache** (`cache` export)
  - `env`: `CACHE_HOST`, `CACHE_PORT`, `REDIS_DB`
  - `secrets`: `CACHE_PASSWORD`
- **Queue** (`queue` export)
  - `env`: `QUEUE_HOST`, `QUEUE_PORT`, `REDIS_DB`
  - `secrets`: `QUEUE_PASSWORD`
- **Edge (optional)** (`edge` export)
  - `env`: `BACKEND_IP`

Explicit overrides may be provided through the standard `DATABASE_*`,
`CACHE_*`, and `QUEUE_*` environment variables or inventory variables.
When overrides are omitted the service fails if peer exports are missing,
removing the previous hard-coded fallbacks that masked configuration
mistakes.

## Runtime behaviour

- The service contract is defined in [`service.yml`](service.yml) and is
  referenced by the role during rendering and apply operations. The
  framework is therefore free to render Docker Compose, Kubernetes,
  Podman, or Proxmox manifests from the same runtime definition.
- Compose deployments set `deploy.resources` only when
  `erpnext_compose_mode` is `stack`. For local `docker-compose` workflows
  the role emits `mem_limit`/`cpus` values instead.
- Additional environment variables must be supplied via the
  `erpnext_extra_env` and `erpnext_socketio_extra_env` dictionaries. Keys
  are automatically prefixed with `ERPNEXT_EXTRA_` and validated so they
  do not override mandatory configuration.
- Secret values (database password, site administrator password, Redis
  credentials, and URLs containing them) are supplied exclusively via the
  secret environment payload. The role fails if any secret value leaks
  into the non-secret environment configuration.
- Redis endpoints are validated with `redis-cli ping` before runtime
  manifests are rendered. Install `redis-cli` on the controller host when
  enabling these checks.
- External Docker networks declared in `erpnext_networks` must exist prior
  to rendering. The role validates their presence via the Docker API.

## Operational guidance

- `erpnext_wait_for_services_timeout_multiplier` scales the base
  bootstrap timeout (600 seconds) and should be increased for slower
  environments. Typical durations:
  - Database initialisation: ~2 minutes
  - Site creation: 6–12 minutes depending on storage throughput
  - Migrations: 4–8 minutes per release train
- Set `erpnext_proxy_configured=true` after provisioning an ingress layer
  capable of injecting the appropriate `X-Forwarded-*` headers. Deployments
  without a proxy should flip `erpnext_require_proxy` to `false` only when
  alternative protections are in place.
- Persistent data is stored in the `erpnext-sites` and `erpnext-assets`
  volumes. Ensure these are backed by durable storage; ephemeral tmpfs
  mounts are provisioned for logs, caches, and temporary directories.

## Testing

Unit tests covering semantic version enforcement live in
[`roles/service/tests`](roles/service/tests). Run them locally with:

```bash
pytest
```

Python sources should be formatted with [Black](https://black.readthedocs.io/) prior to commits.
