import json

from django.conf import settings
from django.db import connection
from django.http import HttpResponse


class HealthCheckMiddleware:
    """/healthz = liveness (process is up), /readyz = readiness (DB reachable)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/healthz":
            return self._json({"status": "ok", "version": settings.APP_VERSION})
        if request.path == "/readyz":
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
            except Exception as exc:  # noqa: BLE001 - any failure means "not ready"
                return self._json({"status": "unavailable", "database": type(exc).__name__}, 503)
            return self._json({"status": "ok", "database": "ok", "version": settings.APP_VERSION})
        return self.get_response(request)

    @staticmethod
    def _json(payload, status=200):
        return HttpResponse(json.dumps(payload), status=status, content_type="application/json")
