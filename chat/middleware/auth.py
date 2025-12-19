from django.contrib.auth.middleware import LoginRequiredMiddleware
from django.conf import settings
from urllib.parse import urlparse, parse_qs, urlencode

import re


class LoginRequiredWithExceptionsMiddleware(LoginRequiredMiddleware):
    """
    Middleware to Require Authentication, while allowing exceptions
    in settings

    Create exceptions with the "@login_not_required" decorator,
    or in settings "LOGIN_REQUIRED_URL_EXCEPTIONS"
    """

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


class HtmxAuthRedirectMiddleware:
    """
    Middleware to handle HTMX authentication redirects properly.

    When an HTMX request results in a 302 redirect (typically for authentication),
    this middleware:
    1. Changes the response status code to 204 (No Content)
    2. Adds an HX-Redirect header with the redirect URL
    3. Preserves the original request path in the 'next' query parameter

    This ensures that after authentication, the user is returned to the page
    they were attempting to access, maintaining a seamless UX with HTMX.

    Credits: https://www.caktusgroup.com/blog/2022/11/11/how-handle-django-login-redirects-htmx/
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # HTMX request returning 302 likely is login required.
        # Take the redirect location and send it as the HX-Redirect header value,
        # with 'next' query param set to where the request originated. Also change
        # response status code to 204 (no content) so that htmx will obey the
        # HX-Redirect header value.

        if request.headers.get("HX-Request") == "true" and response.status_code == 302:
            # Determine the next path from referer or current request path
            ref_header = request.headers.get("Referer", "")
            if ref_header:
                referer = urlparse(ref_header)
                next_path = referer.path
            else:
                next_path = request.path

            # Parse the redirect url
            redirect_url = urlparse(response["Location"])

            # Set response code to 204 for HTMX to process the redirect
            response.status_code = 204

            # Update the "?next" query parameter
            query_params = parse_qs(redirect_url.query)
            query_params["next"] = [next_path]
            new_query = urlencode(query_params, doseq=True)

            # Set the new HX-Redirect header
            response.headers["HX-Redirect"] = f"{redirect_url.path}?{new_query}"

        return response
