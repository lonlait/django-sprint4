from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.shortcuts import get_object_or_404

from .models import Comment
from .forms import CommentForm


class AuthorRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки авторства."""

    def test_func(self):
        return self.get_object().author == self.request.user

    def handle_no_permission(self):
        return redirect("blog:post_detail", post_id=self.kwargs["post_id"])


class CommentMixin(LoginRequiredMixin, AuthorRequiredMixin):
    """Базовый миксин для представлений комментариев."""

    template_name = "blog/comment.html"
    login_url = "login"
    context_object_name = "comment"

    def get_object(self):
        return get_object_or_404(
            Comment,
            id=self.kwargs["comment_id"],
            post_id=self.kwargs["post_id"]
        )

    def get_success_url(self):
        return reverse(
            "blog:post_detail",
            kwargs={"post_id": self.kwargs["post_id"]}
        )


class CommentUpdateMixin(CommentMixin):
    """Без него падают тесты."""

    form_class = CommentForm
