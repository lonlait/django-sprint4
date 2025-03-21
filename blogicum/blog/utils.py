from django.db.models import Count
from django.utils import timezone
from django.core.paginator import Paginator
from django.conf import settings

from .models import Post


def get_post_queryset(
    queryset=Post.objects,
    filter_published=False,
    annotate_comments=False
):
    """
    Возвращает оптимизированный queryset для постов.

    Аргументы:
        queryset: Менеджер модели Post или связанный
            queryset
        filter_published: Если True, фильтрует только
            опубликованные посты
        annotate_comments: Если True, добавляет аннотацию
            с количеством комментариев

    Возвращает:
        QuerySet: Оптимизированный queryset с примененными
            фильтрами и аннотациями
    """
    queryset = queryset.select_related(
        "author",
        "category",
        "location"
    )

    if filter_published:
        queryset = queryset.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )

    if annotate_comments:
        queryset = queryset.annotate(
            comment_count=Count("comments")
        )

    return queryset.order_by("-pub_date")


def get_paginator_page(queryset, request):
    """Получает объект страницы для пагинации."""
    paginator = Paginator(queryset, settings.PAGINATOR_VALUE)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)
