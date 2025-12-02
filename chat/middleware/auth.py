from django.contrib.auth.middleware import LoginRequiredMiddleware
from django.conf import settings
import re


class LoginRequiredWithExceptionsMiddleware(LoginRequiredMiddleware):
    def __init__(self, get_response):
        super().__init__(get_response)
        # Compile the regex patterns
        self.exempt_urls = [
            re.compile(pattern) for pattern in settings.LOGIN_REQUIRED_URL_EXCEPTIONS
        ]

    def process_view(self, request, view_func, view_args, view_kwargs):
        path = request.path_info
        # First check our exempt urls
        if any(pattern.match(path) for pattern in self.exempt_urls):
            return None

        # Otherwise continue with the normal url check
        return super().process_view(request, view_func, view_args, view_kwargs)
