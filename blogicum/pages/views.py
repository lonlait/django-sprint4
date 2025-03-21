from django.shortcuts import render
from django.views.generic.base import TemplateView


class AboutView(TemplateView):
    template_name = 'pages/about.html'


class RulesView(TemplateView):
    template_name = 'pages/rules.html'


def about(request):
    return render(request, "pages/about.html")


def rules(request):
    return render(request, "pages/rules.html")


def csrf_failure(request, reason=""):
    return render(request, "pages/403csrf.html", status=403)


def page_not_found(request, exception):
    """Обработчик ошибки 404."""
    return render(request, 'pages/404.html', status=404)


def server_error(request):
    """Обработчик ошибки 500."""
    return render(request, 'pages/500.html', status=500)


def permission_denied(request, exception):
    """Обработчик ошибки 403."""
    return render(request, 'pages/403csrf.html', status=403)
