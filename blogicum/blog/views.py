from django.conf import settings
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect
from django.views.generic import (
    ListView, UpdateView, CreateView, DeleteView, DetailView
)

from .models import Category, Post, Comment
from .forms import PostForm, CommentForm, UserForm, UserRegistrationForm
from .utils import get_post_queryset, get_paginator_page
from .mixins import AuthorRequiredMixin, CommentMixin, CommentUpdateMixin

User = get_user_model()
PAGE_NUMBER = "page"


class PostListView(ListView):
    """Отображает список опубликованных постов."""

    model = Post
    template_name = "blog/index.html"
    paginate_by = settings.PAGINATOR_VALUE

    def get_queryset(self):
        return get_post_queryset(
            filter_published=True,
            annotate_comments=True
        )


class PostDetailView(DetailView):
    """Отображает детальную информацию о посте."""

    model = Post
    template_name = "blog/detail.html"
    pk_url_kwarg = "post_id"
    login_url = "login"

    def get_object(self, queryset=None):
        post = get_object_or_404(
            get_post_queryset(),
            pk=self.kwargs[self.pk_url_kwarg]
        )
        is_author = post.author == self.request.user
        if not is_author:
            post = get_object_or_404(
                get_post_queryset(filter_published=True),
                pk=self.kwargs[self.pk_url_kwarg]
            )
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = (
            self.object.comments.select_related("author")
            .order_by("created_at")
        )
        return context


@login_required
def category_posts(request, category_slug):
    template = "blog/category.html"
    category = get_object_or_404(
        Category.objects.filter(slug=category_slug),
        is_published=True,
    )
    posts = get_post_queryset(
        category.posts,
        filter_published=True,
        annotate_comments=True
    )
    page_obj = get_paginator_page(posts, request)
    context = {
        "category": category,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile_detail(request, username):
    template = "blog/profile.html"
    profile = get_object_or_404(User, username=username)
    posts = get_post_queryset(
        profile.posts,
        filter_published=request.user.username != username,
        annotate_comments=True
    )
    page_obj = get_paginator_page(posts, request)
    context = {
        "profile": profile,
        "page_obj": page_obj,
        "user": request.user
    }
    return render(request, template, context)


@login_required
def edit_profile(request):
    form = UserForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        return redirect(
            "blog:profile",
            username=request.POST.get("username")
        )
    return render(request, "blog/user.html", {"form": form})


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста."""

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    login_url = "login"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "blog:profile",
            kwargs={"username": self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, AuthorRequiredMixin, UpdateView):
    """Редактирует существующий пост."""

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    login_url = "login"
    pk_url_kwarg = "post_id"

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={"post_id": self.object.pk}
        )


class PostDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    """Удаляет пост."""

    model = Post
    template_name = "blog/post_form.html"
    login_url = "login"
    pk_url_kwarg = "post_id"

    def get_success_url(self):
        return reverse("blog:index")


class CommentUpdateView(CommentUpdateMixin, UpdateView):
    """Представление для обновления комментария."""


class CommentDeleteView(CommentMixin, DeleteView):
    """Удаление комментария."""


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Представление для создания нового комментария."""

    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    login_url = "login"

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs["post_id"]
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={"post_id": self.kwargs["post_id"]}
        )


class UserRegistrationView(CreateView):
    """Регистрация нового пользователя."""

    form_class = UserRegistrationForm
    template_name = "registration/registration_form.html"
    success_url = reverse_lazy("login")


class MyLogoutView(LogoutView):
    """Делает выход доступным через GET запрос."""

    http_method_names = ["get", "post", "options"]

    def get(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


def my_logout_then_login(request, login_url=None):
    """Выход из системы и перенаправление на страницу входа."""
    logout(request)
    return HttpResponseRedirect(login_url or reverse_lazy("login"))
