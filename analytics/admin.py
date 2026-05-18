from django.contrib import admin
from .models import HealthData, FitnessGoal

@admin.register(HealthData)
class HealthDataAdmin(admin.ModelAdmin):
    list_display = ('user', 'weight_kg', 'bmi', 'date')
    list_filter = ('date',)
    search_fields = ('user__username',)

@admin.register(FitnessGoal)
class FitnessGoalAdmin(admin.ModelAdmin):
    list_display = ('user', 'goal_type', 'target_metric', 'current_value', 'status', 'deadline')
    list_filter = ('goal_type', 'status')