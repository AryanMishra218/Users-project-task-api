"""
Why this file exists:
Instead of every route writing its own error response by hand
(and risking inconsistent formats), we define ONE custom
exception, `ApiError`. Any route can just do:

    raise ApiError("Email is required", status_code=400)

...and a single handler (registered in app/__init__.py) catches
it and turns it into a consistent JSON response, every time.
"""


class ApiError(Exception):
    def __init__(self, message, status_code=400, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details  # optional: extra info, e.g. which field failed

    def to_dict(self):
        body = {"error": self.message}
        if self.details:
            body["details"] = self.details
        return body
