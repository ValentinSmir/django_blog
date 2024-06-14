from django.db import models

from django.utils import timezone

from django.contrib.auth import get_user_model

User = get_user_model()


class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(pub_date__lte=timezone.now(),
                                             is_published=True,
                                             category__is_published=True
                                             ).select_related(
            'location', 'author', 'category')


class BaseModel(models.Model):
    is_published = models.BooleanField(
        default=True, verbose_name='Опубликовано',
        help_text='Снимите галочку, чтобы скрыть публикацию.'
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name='Добавлено'
    )

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    description = models.TextField(verbose_name='Описание')
    slug = models.SlugField(
        unique=True, verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; разрешены символы латиницы,'
            ' цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.title


class Location(BaseModel):
    name = models.CharField(max_length=256, verbose_name='Название места')

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'

    def __str__(self):
        return self.name


class Post(BaseModel):
    objects = models.Manager()
    published = PostManager()
    title = models.CharField(max_length=256, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст')
    image = models.ImageField(upload_to='posts_images', blank=True,
                              verbose_name='Фото')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации',
        help_text=(
            'Если установить дату и '
            'время в будущем — можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=False,
        verbose_name='Автор публикации',
        related_name='posts'
    )
    location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, blank=True, null=True,
        verbose_name='Местоположение', related_name='posts'
    )
    category = models.ForeignKey(
        Category, null=True, on_delete=models.SET_NULL,
        verbose_name='Категория', related_name='posts'
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user)


class Comment(models.Model):
    text = models.TextField(
        verbose_name='Комментарии',
        help_text=('Здесь можно написать содержимое комментария')
    )
    post = models.ForeignKey(
        Post, null=True, on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Публикация',
        help_text=('Публикация, к которой привязан комментарий')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата и время отправки коментария',
        help_text=('Дата и время, когда был отправлен комментарий')
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               verbose_name='Автор',
                               help_text=('Автор комментария')
                               )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('created_at',)
