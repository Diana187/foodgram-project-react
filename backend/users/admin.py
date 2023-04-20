from django.contrib import admin

from users.models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username', 'email', 
    )
    list_filter = (
        'username', 'email',
    )
    list_per_page = 5
    search_fields = (
        'username', 'email',
    )
