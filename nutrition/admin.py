from django.contrib import admin
from .models import Meal, Nutrition

@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ('user', 'food_name', 'meal_type', 'calories', 'date')
    list_filter = ('meal_type', 'date')

@admin.register(Nutrition)
class NutritionAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'total_calories_intake')