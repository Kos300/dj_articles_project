from django.db import models
from django.contrib.auth.models import User
from .middleware import get_current_user
from django.db.models import Q


class Articles(models.Model):
    # поле автор имеет связь: 1 автор ко многим статьям
    # on_delete=models.CASCADE - при вызове функции удалим каскад
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Владелец статьи', blank=True, null=True)
    create_date = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(verbose_name='Текст')

    def __str__(self):
        # формат отображения списка в админ панели django
        # return '%s: %s-%s' % (self.create_date, self.name, self.text)
        return self.name

    class Meta:
        verbose_name = 'Статью'
        verbose_name_plural = 'Статьи'


# класс для вывода комментариев согласно условиям из класса Comments
class StatusFilterComments(models.Manager):
    # переопределим метод
    def get_queryset(self):
        # запишем наборы условий через Q
        # автор коммента видит свои не опублк комменты
        # автор статьи видит все комменты к статье
        # все пользователи видят опубликованные True комменты
        return super().get_queryset().filter(Q(status=False, author = get_current_user()) | Q(status=False, article__author=get_current_user()) | Q(status=True))


class Comments(models.Model):
    article = models.ForeignKey(Articles, on_delete=models.CASCADE, verbose_name='Статья', blank=True, null=True, related_name='comments_article')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор комментария', blank=True, null=True)
    create_date = models.DateTimeField(auto_now=True)
    text = models.TextField(verbose_name='Текст комментария')
    # для модерации комментариев
    status = models.BooleanField(verbose_name='Видимость статьи', default=False)
    # вызов комментариев согласно условиям через Comments.objects.all()
    objects = StatusFilterComments()


