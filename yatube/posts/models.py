from django.db import models
from django.contrib.auth import get_user_model

from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название группы',
    )
    slug = models.SlugField(
        unique=True,
        max_length=20,
        verbose_name='URL адреса группы'
    )
    description = models.TextField(
        verbose_name='Описание группы',
    )

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст вашего поста'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='select',
        help_text='Выберите группу или оставьте пустым',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='image',
    )

    @property
    def get_author_post(self):
        return self.author.posts.all().count()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Post',
    )
    author = models.ForeignKey(
        User,
        blank=False,
        null=False,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )

    class Meta:
        verbose_name = 'comment'
        verbose_name_plural = 'comments'

    def __str__(self):
        comment_text = self.text[:20]
        return f'Комментарий {comment_text}'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
