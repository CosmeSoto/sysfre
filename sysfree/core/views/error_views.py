from django.shortcuts import render


def error_400(request, exception):
    """Vista para el error 400 (Bad Request)."""
    return render(request, 'core/errors/400.html', status=400)


def error_403(request, exception):
    """Vista para el error 403 (Forbidden)."""
    return render(request, 'core/errors/403.html', status=403)


def error_404(request, exception):
    """Vista para el error 404 (Not Found)."""
    return render(request, 'core/errors/404.html', status=404)


def error_500(request):
    """Vista para el error 500 (Server Error)."""
    return render(request, 'core/errors/500.html', status=500)