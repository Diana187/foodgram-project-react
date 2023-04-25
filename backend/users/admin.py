from django.contrib import admin

from users.models import User, Follow

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email', 
    )
    list_filter = (
        'username',
        'email',
    )
    search_fields = (
        'username',
        'email',
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('username', 'following', 'email', )
    list_filter = ('username', )
    search_fields = ('username', 'email', )
    ordering = ('username', )
