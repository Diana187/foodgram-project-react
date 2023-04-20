from django.db import models

from colorfield.fields import ColorField

from users.models import User


class Ingridient(models.Model):
    name = models.CharField(
        'Название ингридиента',
        max_length=200,
    )
    measure = models.CharField(
        'Единицы измерения',
        max_length=200,
    )

    class Meta:
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name} {self.measure}'


class Tag(models.Model):
    name = models.CharField(
        'Название тега',
        max_length=200,
        unique=True
    )
    color = ColorField(
        'Цветовой HEX-код',
        default='#49B64E',
        format='hex',
        max_length=7,
        unique=True

    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор рецепта',
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    name = models.CharField(
        'Название рецепта',
        max_length=200,
        help_text='Добавьте название рецепта',
    )
    image = models.ImageField(
        'Изображение рецепта',
        help_text='Добавьте фотографию рецепта',
        upload_to='recipes/image/',
        null=True,
        default=None,
    )
    text = models.TextField(
        'Описание рецепта',
        max_length=500,
        help_text='Добавьте описание к рецепту',
    )
    ingridients = models.ManyToManyField(
        Ingridient,
        related_name='recipes',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги рецептов',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время готовкив минутах',
        default=1,
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return f'{self.name} {self.author}'
