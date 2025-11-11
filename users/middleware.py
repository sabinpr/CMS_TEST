from django.utils import timezone
from datetime import timedelta


class LastActiveMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        user = getattr(request, "user", None)
        if getattr(user, "is_authenticated", False) and request.path.startswith(
            "/api/"
        ):
            # Update only if more than 1 minute has passed
            if not user.last_active or timezone.now() - user.last_active > timedelta(
                minutes=1
            ):
                user.last_active = timezone.now()
                user.save(update_fields=["last_active"])

        return response
