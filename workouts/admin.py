from django.contrib import admin
from .models import Workout

@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ('user', 'workout_type', 'duration_minutes', 'calories_burned', 'date')
    list_filter = ('workout_type', 'intensity', 'date')
    search_fields = ('user__username',)