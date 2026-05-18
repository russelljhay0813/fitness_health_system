from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Sum, Count, Avg
from datetime import date, timedelta
from workouts.models import Workout
from nutrition.models import Meal, Nutrition
from analytics.models import HealthData, FitnessGoal, HealthAnalyzer
from users.models import UserProfile
from django.utils import timezone

@login_required
def dashboard(request):
    """Main dashboard with analytics and insights"""
    user = request.user
    today = date.today()
    
    # Get today's data
    today_workouts = Workout.objects.filter(user=user, date=today)
    today_meals = Meal.objects.filter(user=user, date=today)
    today_nutrition, created = Nutrition.objects.get_or_create(user=user, date=today)
    today_nutrition.update_totals()
    
    today_calories_burned = sum(w.calories_burned for w in today_workouts)
    today_calories_intake = today_nutrition.total_calories_intake
    
    # Weekly summary
    week_ago = today - timedelta(days=7)
    weekly_workouts = Workout.objects.filter(user=user, date__gte=week_ago)
    weekly_calories_burned = sum(w.calories_burned for w in weekly_workouts)
    
    # Latest weight
    latest_weight = HealthData.objects.filter(user=user).order_by('-date').first()
    
    # Active goals
    active_goals = FitnessGoal.objects.filter(user=user).exclude(status='completed')
    
    # Initialize analyzer
    analyzer = HealthAnalyzer(user)
    insights = analyzer.get_personalized_insights()
    
    context = {
        'today_workouts': today_workouts,
        'today_meals': today_meals,
        'today_calories_intake': today_calories_intake,
        'today_calories_burned': today_calories_burned,
        'weekly_workouts_count': weekly_workouts.count(),
        'weekly_calories_burned': weekly_calories_burned,
        'latest_weight': latest_weight,
        'active_goals': active_goals,
        'insights': insights,
    }
    
    return render(request, 'core/dashboard.html', context)

@login_required
def analytics_view(request):
    """Analytics and visualization dashboard"""
    user = request.user
    analyzer = HealthAnalyzer(user)
    
    workout_trends = analyzer.get_workout_trends()
    weight_trends = analyzer.get_weight_trends()
    calorie_trends = analyzer.get_calorie_balance_trend()
    progress_rate = analyzer.calculate_progress_rate()
    insights = analyzer.get_personalized_insights()
    
    # Goals data for charts
    goals = FitnessGoal.objects.filter(user=user)
    goals_data = [
        {
            'name': goal.get_goal_type_display(),
            'progress': goal.calculate_progress(),
            'target': goal.target_metric,
            'current': goal.current_value
        }
        for goal in goals
    ]
    
    context = {
        'workout_trends': workout_trends,
        'weight_trends': weight_trends,
        'calorie_trends': calorie_trends,
        'progress_rate': progress_rate,
        'insights': insights,
        'goals_data': goals_data,
    }
    
    return render(request, 'core/analytics.html', context)

class WorkoutCreateView(LoginRequiredMixin, CreateView):
    model = Workout
    fields = ['workout_type', 'duration_minutes', 'intensity', 'notes']
    template_name = 'core/workout_form.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Workout logged successfully!')
        return super().form_valid(form)

class MealCreateView(LoginRequiredMixin, CreateView):
    model = Meal
    fields = ['meal_type', 'food_name', 'calories', 'protein', 'carbs', 'fat']
    template_name = 'core/meal_form.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        # Update nutrition totals for the day
        nutrition, created = Nutrition.objects.get_or_create(
            user=self.request.user,
            date=date.today()
        )
        nutrition.update_totals()
        messages.success(self.request, 'Meal added successfully!')
        return response

class HealthDataCreateView(LoginRequiredMixin, CreateView):
    model = HealthData
    fields = ['weight_kg']
    template_name = 'core/weight_form.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Weight logged successfully!')
        return super().form_valid(form)

class GoalCreateView(LoginRequiredMixin, CreateView):
    model = FitnessGoal
    fields = ['goal_type', 'target_metric', 'deadline']
    template_name = 'core/goal_form.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Goal created successfully!')
        return super().form_valid(form)

class GoalUpdateView(LoginRequiredMixin, UpdateView):
    model = FitnessGoal
    fields = ['current_value']
    template_name = 'core/goal_update.html'
    success_url = reverse_lazy('dashboard')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.update_status()
        messages.success(self.request, 'Goal progress updated!')
        return response