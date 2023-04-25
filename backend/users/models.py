from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    first_name = models.CharField(
        'Имя',
        max_length=200,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=200,
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=200,
        validators=(UnicodeUsernameValidator(),),
        unique=True,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=200,
        unique=True,
    )

    class Meta:
        verbose_name='Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('first_name', 'last_name',)


    def __str__(self):
        return self.username


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Подписка',
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_followers',
            ),
        )
        ordering = ('-id', )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self) -> str:
        return f'{self.user} подписан на {self.following}'
