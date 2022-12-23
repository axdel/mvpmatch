from functools import wraps

from rest_framework.exceptions import APIException


def allowed_role(role):
    def decorator(function):
        @wraps(function)
        def wrapper(self, request, *args, **kwargs):
            if request.user.role == role:
                return function(self, request, *args, **kwargs)
            else:
                raise APIException(f'Only {role} role is allowed for this endpoint.')
        return wrapper
    return decorator