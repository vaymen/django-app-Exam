# django-app

Minimal Django application with a production-ready Dockerfile. Part of a three-repo deployment set:
[Ansible](https://github.com/vaymen/django-ansible-Exam) · [Helm](https://github.com/vaymen/django-helm-Exam).

## Contents

| Path | Purpose |
|---|---|
| `config/settings.py` | all settings come from environment variables; nothing hard-coded |
| `config/views.py` | welcome page (database status, version, pod name) |
| `config/health.py` | `/healthz` and `/readyz` middleware |
| `Dockerfile` | multi-stage build, virtualenv, non-root (UID 10001), gunicorn, `HEALTHCHECK` |

## Configuration

| Variable | Required | Description |
|---|---|---|
| `DJANGO_SECRET_KEY` | yes | the app refuses to start without it (intentionally) |
| `DB_HOST`, `DB_NAME`, `DB_USER`, `DB_PASSWORD` | yes | PostgreSQL connection |
| `DB_PORT` | no | default `5432` |
| `DJANGO_ALLOWED_HOSTS` | no | comma-separated, default `localhost,127.0.0.1` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | no | e.g. `https://app.example.com` |
| `DJANGO_BEHIND_PROXY` | no | `true` behind a TLS-terminating proxy or ingress |
| `DJANGO_DEBUG` | no | default `false` |
| `APP_VERSION` | no | shown on the page and in `/healthz` (the image tag) |
| `WEB_CONCURRENCY` | no | gunicorn workers |
| `DJANGO_LOG_LEVEL`, `DB_CONN_MAX_AGE`, `DB_CONNECT_TIMEOUT` | no | optional tuning |

## Build and publish (tag = commit id)

```bash
TAG=$(git rev-parse --short HEAD)
docker build -t docker.io/vaymen/django-app:$TAG .
docker login -u vaymen
docker push docker.io/vaymen/django-app:$TAG
```

## Run

```bash
docker network create demo
docker run -d --name pg --network demo \
  -e POSTGRES_PASSWORD=demo -e POSTGRES_DB=django postgres:16-alpine
docker run --rm --network demo -p 8000:8000 \
  -e DJANGO_SECRET_KEY=dev-only -e DB_HOST=pg -e DB_NAME=django \
  -e DB_USER=postgres -e DB_PASSWORD=demo -e DJANGO_ALLOWED_HOSTS=localhost \
  docker.io/vaymen/django-app:$TAG
```

- `http://localhost:8000/` welcome page
- `/healthz` liveness (no dependencies)
- `/readyz` readiness (`503` when the database is unreachable)

## Running in different environments

| Environment | Notes |
|---|---|
| Local | `DJANGO_ALLOWED_HOSTS=localhost`; `DJANGO_DEBUG=true` for debugging |
| Single VM (Compose) | use the [ansible repo](https://github.com/vaymen/django-ansible-Exam); database runs in the same Compose project |
| Kubernetes | use the [helm repo](https://github.com/vaymen/django-helm-Exam); configuration comes from a ConfigMap and Secrets |
| Behind a load balancer / ingress | set `DJANGO_BEHIND_PROXY=true` and `DJANGO_CSRF_TRUSTED_ORIGINS` |
| Managed database (RDS, Cloud SQL, ...) | point the `DB_*` variables at it |

## Design decisions

- **Separate build stage with a virtualenv.** The final image has no compiler or pip cache; `psycopg[binary]` removes the need for `libpq-dev`.
- **gunicorn instead of `runserver`**, with `--worker-tmp-dir /dev/shm` so the root filesystem can be read-only.
- **Welcome page served with `DEBUG=False`.** Health routes sit first in the middleware stack, so probes work with the pod IP as `Host` without touching `ALLOWED_HOSTS`.
- **Possible, but unnecessary here:** WhiteNoise for static files, `pip-tools` with hashes for a fully locked dependency set, pinning the base image by digest.

## How this was built

Written with the help of an AI coding assistant (Claude Code) and reviewed by hand. The image was built, run against PostgreSQL and deployed on kind. [`AGENTS.md`](AGENTS.md) records the conventions and commands an agent must follow when changing this repository.
