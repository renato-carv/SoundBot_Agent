from functools import wraps

def require_connection(attr_name: str = "sp", service_name: str = "Service"):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if not getattr(self, attr_name, None):
                return [f"{service_name} is not available at the moment"]
            return func(self, *args, **kwargs)
        return wrapper
    return decorator
