from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('workout/add/', views.WorkoutCreateView.as_view(), name='add_workout'),
    path('meal/add/', views.MealCreateView.as_view(), name='add_meal'),
    path('weight/add/', views.HealthDataCreateView.as_view(), name='add_weight'),
    path('goal/add/', views.GoalCreateView.as_view(), name='add_goal'),
    path('goal/<int:pk>/update/', views.GoalUpdateView.as_view(), name='update_goal'),
]