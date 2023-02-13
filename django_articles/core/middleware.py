from django.utils.deprecation import MiddlewareMixin

# используем многопоточность threading
import threading
_local_storage = threading.local()


# в settings добавлен путь к этому файлу в MIDDLEWARE
class CurrentRequestMiddlewareUser(MiddlewareMixin):
    def process_request(self, request):
        # request.user # имя пользователя из запроса
        # request сохранен в _local_storage.request
        _local_storage.request = request


def get_current_request():
    return getattr(_local_storage, 'request', None)


def get_current_user():
    request = get_current_request()
    if request is None:
        return None
    return getattr(request, 'user', None)

