from __future__ import annotations

from django.conf import settings
from django.http import HttpResponse
from django.utils.cache import patch_vary_headers


class DevCorsMiddleware:
    """
    Minimal CORS middleware for local development.

    This keeps the project dependency-free (no django-cors-headers) while
    allowing the Next.js dev server (typically http://localhost:3000) to call
    the Django API on http://127.0.0.1:8000.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.headers.get("Origin")
        allowed_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])

        is_allowed = bool(origin) and origin in allowed_origins
        if request.method == "OPTIONS" and is_allowed:
            response = HttpResponse(status=200)
        else:
            response = self.get_response(request)

        if not is_allowed:
            return response

        response["Access-Control-Allow-Origin"] = origin
        response["Access-Control-Allow-Methods"] = ", ".join(
            getattr(
                settings,
                "CORS_ALLOWED_METHODS",
                ["DELETE", "GET", "OPTIONS", "PATCH", "POST", "PUT"],
            )
        )
        response["Access-Control-Allow-Headers"] = ", ".join(
            getattr(
                settings,
                "CORS_ALLOWED_HEADERS",
                [
                    "authorization",
                    "content-type",
                    "accept",
                    "origin",
                    "x-requested-with",
                ],
            )
        )
        response["Access-Control-Max-Age"] = "600"
        patch_vary_headers(response, ("Origin",))
        return response

