from django.contrib.auth.models import AbstractUser
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
        unique=True,
    )
    email = models.EmailField(
        'Электронная почта',
        max_length=200,
        unique=True,
    )

    def __str__(self):
        return self.username
# EmailValidator?

