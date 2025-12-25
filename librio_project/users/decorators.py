from django.http import HttpResponseForbidden
from django.shortcuts import redirect


def librarian_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        if not hasattr(request.user, 'userprofile'):
            return HttpResponseForbidden("Доступ запрещен. У вас нет профиля пользователя.")

        user_type = request.user.userprofile.user_type
        if user_type in ['admin', 'librarian']:
            return view_func(request, *args, **kwargs)

        return HttpResponseForbidden(
            f"Доступ запрещен. Ваш тип пользователя: '{user_type}'. Требуется 'librarian' или 'admin'.")

    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)

        if not hasattr(request.user, 'userprofile'):
            return HttpResponseForbidden("Доступ запрещен. У вас нет профиля пользователя.")

        if request.user.userprofile.user_type == 'admin':
            return view_func(request, *args, **kwargs)

        return HttpResponseForbidden(
            f"Доступ запрещен. Ваш тип пользователя: '{request.user.userprofile.user_type}'. Требуется 'admin'.")

    return wrapper