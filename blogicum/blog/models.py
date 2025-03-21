from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

TITLE_MAX_LENGTH = 256


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию."
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Добавлено"
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name="Заголовок"
    )
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text=(
            "Идентификатор страницы для URL; разрешены символы латиницы, "
            "цифры, дефис и подчёркивание."
        )
    )

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title[:50]


class Location(BaseModel):
    name = models.CharField(
        max_length=TITLE_MAX_LENGTH,
        verbose_name="Location"
    )

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name[:50]


class Post(BaseModel):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    title = models.CharField(
        max_length=256,
        verbose_name="Заголовок",
        default=""
    )
    text = models.TextField(
        verbose_name="Текст",
    )
    pub_date = models.DateTimeField(
        verbose_name="Дата и время ",
        help_text=(
            "Если установить дату и время в будущем — "
            "можно делать отложенные публикации."
        )
    )
    image = models.ImageField(
        verbose_name="Изображение",
        upload_to="post_images",
        blank=True
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Местоположение"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Категория"
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        default_related_name = "posts"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.title[:50]


class Comment(BaseModel):
    text = models.TextField("Текст комментария", max_length=256)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Пост",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор комментария",
    )
    created_at = models.DateTimeField(
        "Добавлено",
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        verbose_name = "комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ("-created_at",)

    def __str__(self):
        return f"Комментарий пользователя {self.author} к посту {self.post}"
