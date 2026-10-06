# AGENTS.md — django-app

Minimal Django app + production Dockerfile. Sibling repos: `django-ansible-Exam` (Compose on a VM), `django-helm-Exam` (Kubernetes). All three deploy the **same image**.

## Layout
- `config/settings.py` — every setting comes from an environment variable.
- `config/views.py` — welcome page (Persian, RTL); shows DB status, version, pod name.
- `config/health.py` — `/healthz` (liveness) and `/readyz` (readiness) middleware, first in `MIDDLEWARE`.
- `Dockerfile` — multi-stage, venv, non-root UID 10001, gunicorn.

## Commands
```bash
TAG=$(git rev-parse --short HEAD)
docker build -t docker.io/vaymen/django-app:$TAG .
docker push docker.io/vaymen/django-app:$TAG        # needs `docker login` (done by the human)
```
Smoke test: run the image next to `postgres:16-alpine` (see README), then `curl localhost:8000/readyz` must return 200.

## Rules
- No hard-coded environment config; add a new env var to `settings.py` **and** the README table.
- `/healthz` must never touch the database (a DB outage must not restart pods). `/readyz` must.
- Image tag = git commit id. Never use `latest`. After pushing a new image, update the tag in the ansible and helm repos.
- Keep the image non-root and compatible with a read-only root filesystem (no writes outside `/tmp` and `/dev/shm`).
- Never commit secrets, `.env` files or credentials.
- README stays in English; the welcome page text is Persian on purpose.
- Keep it simple: do not add dependencies or components without a clear reason.
