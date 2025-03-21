from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.http import Http404, HttpResponse
from django.utils import timezone
from django.views.generic import (
    ListView, UpdateView, CreateView, DeleteView, DetailView
)

from .models import Category, Post, Comment
from .forms import PostForm, CommentForm, UserForm

User = get_user_model()
PAGINATOR_VALUE = 10
PAGE_NUMBER = "page"


def post_queryset(category_is_published: bool = True):
    return Post.objects.select_related("author", "category").filter(
        is_published=True,
        pub_date__lte=timezone.now(),
        category__is_published=category_is_published
    ).order_by("-pub_date")


@login_required
def simple_view(request):
    return HttpResponse("Страница для залогиненных пользователей!")


def get_page_context(queryset, request):
    paginator = Paginator(queryset, PAGINATOR_VALUE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return {
        "paginator": paginator,
        "page_number": page_number,
        "page_obj": page_obj,
    }


class PostListView(ListView):
    model = Post
    template_name = "blog/index.html"
    queryset = (
        Post.objects.select_related("author", "category")
        .filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
        .annotate(comment_count=Count("comments"))
    )
    ordering = "-pub_date"
    paginate_by = PAGINATOR_VALUE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = "blog/detail.html"
    pk_url_kwarg = "pk"
    login_url = "login"

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        is_author = (
            self.request.user.is_authenticated
            and post.author == self.request.user
        )
        if not is_author:
            if not post.is_published or not post.category.is_published:
                raise Http404
            if post.pub_date > timezone.now():
                raise Http404
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = (
            self.object.comments.select_related("author")
        )
        context["user"] = self.request.user
        return context


@login_required
def category_posts(request, category_slug):
    template = "blog/category.html"
    category = get_object_or_404(
        Category.objects.prefetch_related(
            Prefetch(
                "posts",
                post_queryset()
                .annotate(comment_count=Count("comments")),
            )
        ).filter(slug=category_slug),
        is_published=True,
    )
    posts = category.posts.all()
    paginator = Paginator(posts, PAGINATOR_VALUE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "category": category,
        "page_obj": page_obj,
    }
    return render(request, template, context)


def profile_detail(request, username):
    template = "blog/profile.html"
    profile = get_object_or_404(User, username=username)
    posts = Post.objects.select_related("author", "category").filter(
        author__username=username,
    )
    if not (
        request.user.is_authenticated
        and request.user.username == username
    ):
        posts = posts.filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        )
    posts = (
        posts.annotate(comment_count=Count("comments"))
        .order_by("-pub_date")
    )
    paginator = Paginator(posts, PAGINATOR_VALUE)
    page_number = request.GET.get(PAGE_NUMBER)
    page_obj = paginator.get_page(page_number)
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
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    login_url = "login"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile",
            kwargs={"username": self.request.user.username}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PostForm()
        return context


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    login_url = "login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect("blog:post_detail", pk=self.get_object().pk)

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["form"] = PostForm(instance=self.object)
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = "blog/create.html"
    login_url = "login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy("blog:index")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["form"] = PostForm(instance=self.object)
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    login_url = "login"

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs["pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"pk": self.post_object.pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["post"] = self.post_object
        context["user"] = self.request.user
        context["form"] = CommentForm()
        return context


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    login_url = "login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"pk": self.object.post.pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        context["form"] = CommentForm(instance=self.object)
        return context


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Comment
    template_name = "blog/comment.html"
    login_url = "login"

    def test_func(self):
        return self.get_object().author == self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail",
            kwargs={"pk": self.object.post.pk}
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user"] = self.request.user
        return context
