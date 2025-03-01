from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from main import models
from main.models import User, Food, FoodCategory, SizeAndPrice, Addition


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email')
    exclude = ('password', )
    readonly_fields = ('last_login', 'date_joined')


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    pass

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ["title", "id", "description", 'get_food_in_count']
    list_display_links = ["id", "title"]

@admin.register(SizeAndPrice)
class SizeAndPriceAdmin(admin.ModelAdmin):
    pass

@admin.register(Addition)
class AdditionAdmin(admin.ModelAdmin):
    pass