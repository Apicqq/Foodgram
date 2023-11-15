from functools import wraps

def get_related_queryset(related_name, related_object_arg):
    """Декоратор для упаковки повторяющегося кода."""
    def decorator(func):
        @wraps(func)
        def wrapper(self, obj):
            request = self.context.get('request')
            return (request and request.user.is_authenticated
                    and getattr(request.user, related_name).filter(
                        **{related_object_arg: obj}).exists())

        return wrapper

    return decorator

# return request.user.follower.filter(author=obj).exists