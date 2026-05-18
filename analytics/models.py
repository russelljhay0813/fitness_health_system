from django.db import models
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from workouts.models import Workout
from nutrition.models import Nutrition, Meal
from users.models import UserProfile
from django.db.models import Sum, Avg, Count
from decimal import Decimal

User = get_user_model()

class HealthData(models.Model):
    """Weight & BMI Monitoring data"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_data')
    weight_kg = models.FloatField(help_text="Weight in kilograms")
    bmi = models.FloatField(null=True, blank=True)
    date = models.DateField(default=date.today)
    recorded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """Auto-calculate BMI before saving"""
        if self.user.profile and hasattr(self.user, 'profile'):
            self.bmi = self.user.profile.calculate_bmi(self.weight_kg)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.weight_kg}kg - {self.date}"

class FitnessGoal(models.Model):
    """Goal Setting & Progress Monitoring"""
    GOAL_TYPES = (
        ('lose_weight', 'Lose Weight'),
        ('gain_muscle', 'Gain Muscle'),
        ('maintain_fitness', 'Maintain Fitness'),
        ('improve_endurance', 'Improve Endurance'),
    )
    
    STATUS_CHOICES = (
        ('on_track', 'On Track'),
        ('behind', 'Behind'),
        ('completed', 'Completed'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='goals')
    goal_type = models.CharField(max_length=20, choices=GOAL_TYPES)
    target_metric = models.FloatField(help_text="Target value (weight in kg, workout hours, etc.)")
    current_value = models.FloatField(default=0)
    deadline = models.DateField()
    start_date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='on_track')
    
    def calculate_progress(self):
        """Calculate progress percentage"""
        if self.target_metric > 0:
            progress = (self.current_value / self.target_metric) * 100
            return min(100, progress)
        return 0
    
    def update_status(self):
        """Automatic status updates (On Track / Behind / Completed)"""
        if self.current_value >= self.target_metric:
            self.status = 'completed'
        else:
            days_remaining = (self.deadline - date.today()).days
            if days_remaining > 0:
                required_progress_per_day = (self.target_metric - self.current_value) / days_remaining
                if required_progress_per_day < 0:
                    self.status = 'completed'
                else:
                    self.status = 'on_track'
            else:
                self.status = 'behind'
        self.save()
    
    def __str__(self):
        return f"{self.user.username} - {self.goal_type} - {self.status}"

class HealthAnalyzer(models.Model):
    """HealthAnalyzer class processes raw data, calculates trends, and outputs analytics"""
    
    def __init__(self, user):
        self.user = user
    
    def get_workout_trends(self, weeks=4):
        """Analyze workout trends over time"""
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks)
        
        workouts = Workout.objects.filter(
            user=self.user,
            date__range=[start_date, end_date]
        )
        
        weekly_data = {}
        for i in range(weeks):
            week_start = start_date + timedelta(weeks=i)
            week_end = week_start + timedelta(days=6)
            week_workouts = workouts.filter(date__range=[week_start, week_end])
            weekly_data[f'Week {i+1}'] = {
                'count': week_workouts.count(),
                'calories': sum(w.calories_burned for w in week_workouts),
                'duration': sum(w.duration_minutes for w in week_workouts),
            }
        
        return weekly_data
    
    def get_weight_trends(self, months=3):
        """Analyze weight trends over time"""
        end_date = date.today()
        start_date = end_date - timedelta(days=months*30)
        
        weight_data = HealthData.objects.filter(
            user=self.user,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        return [
            {'date': data.date, 'weight': data.weight_kg, 'bmi': data.bmi}
            for data in weight_data
        ]
    
    def get_calorie_balance_trend(self, days=30):
        """Analyze calorie balance over time"""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        nutrition_records = Nutrition.objects.filter(
            user=self.user,
            date__range=[start_date, end_date]
        )
        
        workouts = Workout.objects.filter(
            user=self.user,
            date__range=[start_date, end_date]
        )
        
        trend_data = []
        current_date = start_date
        
        while current_date <= end_date:
            day_nutrition = nutrition_records.filter(date=current_date).first()
            day_workouts = workouts.filter(date=current_date)
            
            calories_burned = sum(w.calories_burned for w in day_workouts)
            calories_intake = day_nutrition.total_calories_intake if day_nutrition else 0
            
            trend_data.append({
                'date': current_date,
                'calories_intake': calories_intake,
                'calories_burned': calories_burned,
                'net_balance': calories_intake - calories_burned
            })
            current_date += timedelta(days=1)
        
        return trend_data
    
    def calculate_progress_rate(self):
        """Calculate progress rate for different metrics"""
        # Get first and last month data
        today = date.today()
        last_month = today - timedelta(days=30)
        two_months_ago = today - timedelta(days=60)
        
        # Workout consistency
        recent_workouts = Workout.objects.filter(
            user=self.user,
            date__range=[last_month, today]
        ).count()
        
        previous_workouts = Workout.objects.filter(
            user=self.user,
            date__range=[two_months_ago, last_month]
        ).count()
        
        if previous_workouts > 0:
            workout_improvement = ((recent_workouts - previous_workouts) / previous_workouts) * 100
        else:
            workout_improvement = 100 if recent_workouts > 0 else 0
        
        # Weight progress
        recent_weight = HealthData.objects.filter(
            user=self.user,
            date__range=[last_month, today]
        ).order_by('-date').first()
        
        previous_weight = HealthData.objects.filter(
            user=self.user,
            date__range=[two_months_ago, last_month]
        ).order_by('-date').first()
        
        weight_change = 0
        if recent_weight and previous_weight:
            weight_change = previous_weight.weight_kg - recent_weight.weight_kg
        
        return {
            'workout_consistency': round(workout_improvement, 1),
            'weight_change': round(weight_change, 1),
            'workout_count_recent': recent_workouts,
            'workout_count_previous': previous_workouts,
        }
    
    def get_personalized_insights(self):
        """Generate personalized health insights"""
        progress = self.calculate_progress_rate()
        insights = []
        
        if progress['workout_consistency'] > 20:
            insights.append(f"Amazing! Workout consistency improved by {progress['workout_consistency']}% this month!")
        elif progress['workout_consistency'] > 0:
            insights.append(f"Good progress! Workout consistency increased by {progress['workout_consistency']}% this month.")
        elif progress['workout_consistency'] < 0:
            insights.append(f"Workout consistency decreased by {abs(progress['workout_consistency'])}% this month. Let's get back on track!")
        else:
            insights.append("Keep pushing! Try to increase your workout frequency this month.")
        
        if progress['weight_change'] > 0:
            insights.append(f"Great job! You've lost {progress['weight_change']}kg this month. Stay consistent!")
        elif progress['weight_change'] < 0:
            insights.append(f"Weight increased by {abs(progress['weight_change'])}kg this month. Consider adjusting your diet or exercise routine.")
        else:
            insights.append("Weight maintained steadily. Focus on your specific goals for better results!")
        
        # Add more insights based on goal achievement
        goals = FitnessGoal.objects.filter(user=self.user, status='on_track')
        if goals.exists():
            insights.append(f"You have {goals.count()} active goals. Keep working towards them!")
        
        return insights