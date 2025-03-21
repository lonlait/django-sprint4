from django.urls import path, include

from . import views

app_name = 'blog'

post_patterns = [
    path('', views.PostListView.as_view(), name='index'),
    path(
        '<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        '<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        '<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'
    ),
]

comment_patterns = [
    path(
        '<int:post_id>/comment/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
]

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('posts/', include(post_patterns)),
    path('posts/', include(comment_patterns)),
    path(
        'category/<slug:category_slug>/',
        views.category_posts,
        name='category_posts'
    ),
    path(
        'profile/<str:username>/',
        views.profile_detail,
        name='profile'
    ),
    path(
        'edit_profile/',
        views.edit_profile,
        name='edit_profile'
    ),
]
