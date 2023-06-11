from colorfield.fields import ColorField
from django.core.validators import MinValueValidator
from django.db import models

from users.models import User


class Ingredient(models.Model):
    """Модель для ингредиентов."""
    name = models.CharField(
        'Название ингредиента',
        db_index=True,
        max_length=200,
    )
    measurement_unit = models.CharField(
        'Единицы измерения',
        max_length=200,
    )
    created = models.DateTimeField(
        'Добавлен',
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        'Изменён',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Ингредиенты'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name} {self.measurement_unit}'


class Tag(models.Model):
    """Модель для тегов."""
    name = models.CharField(
        'Название тега',
        db_index=True,
        max_length=200,
        unique=True,
    )
    color = ColorField(
        'Цветовой HEX-код',
        default='#49B64E',
        format='hex',
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        verbose_name='Слаг',
        unique=True,
    )
    created = models.DateTimeField(
        'Добавлен',
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        'Изменён',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""
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
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты',
        through='RecipeIngredientAmount',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги рецептов',
        related_name='recipes',
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления',
        help_text='Введите время приготовления в минутах',
        default=1,
        validators=[MinValueValidator(1)],
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )
    created = models.DateTimeField(
        'Добавлен',
        auto_now_add=True,
    )
    updated = models.DateTimeField(
        'Изменён',
        auto_now=True,
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date', 'name',)

    def __str__(self):
        return f'{self.name} {self.author}'


class FavoriteShoppingList(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='Рецепт',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='favorite_recipe_user_unique',
            ),
        )

    def __str__(self) -> str:
        return f'{self.user} add {self.recipe} in favorite.'


class ShoppingCart(FavoriteShoppingList):
    """Модель списка покупок."""

    class Meta(FavoriteShoppingList.Meta):
        default_related_name = 'shopping_cart'
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='shoppingcart_recipe_user_unique',
            ),
        )



class Favorite(FavoriteShoppingList):
    """Модель избранного."""

    class Meta(FavoriteShoppingList.Meta):
        default_related_name = 'favorites'
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'


class RecipeIngredientAmount(models.Model):
    """Модель количества ингредиентов в рецепте."""
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredienttorecipe',
        verbose_name='Рецепт',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиентов в рецепте',
        validators=[MinValueValidator(1)],
    )

    class Meta:
        ordering = ('-id', )
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = (
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_amount',
            ),
        )

    def __str__(self):
        return (
            f'{self.ingredient.name} :: {self.ingredient.measurement_unit}'
            f' - {self.amount}')
