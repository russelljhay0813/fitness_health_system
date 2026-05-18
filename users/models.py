from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('user', 'Regular User'),
        ('admin', 'Administrator'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')
    height = models.FloatField(help_text="Height in centimeters", null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def is_admin_user(self):
        return self.role == 'admin' or self.is_superuser
    
    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"

class UserProfile(models.Model):
    """UserProfile class stores and updates core health metrics"""
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    weight_goal = models.FloatField(help_text="Target weight in kg", null=True, blank=True)
    daily_calorie_goal = models.IntegerField(help_text="Daily calorie intake target", default=2000)
    workout_goal_weekly = models.IntegerField(help_text="Weekly workout sessions target", default=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def calculate_bmi(self, weight_kg):
        """Calculate BMI using user height"""
        if self.user.height and weight_kg:
            height_m = self.user.height / 100
            return round(weight_kg / (height_m ** 2), 1)
        return None
    
    def get_bmi_category(self, bmi):
        """BMI category classification"""
        if bmi < 18.5:
            return "Underweight"
        elif 18.5 <= bmi < 25:
            return "Normal"
        elif 25 <= bmi < 30:
            return "Overweight"
        else:
            return "Obese"
    
    def __str__(self):
        return f"{self.user.username}'s Profile"