from django.db import models
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

class Workout(models.Model):
    """Workout class handles data validation, storage, and retrieval"""
    
    WORKOUT_TYPES = (
        ('running', 'Running'),
        ('gym', 'Gym Session'),
        ('cycling', 'Cycling'),
        ('home', 'Home Workout'),
        ('swimming', 'Swimming'),
        ('yoga', 'Yoga'),
        ('other', 'Other'),
    )
    
    INTENSITY_LEVELS = (
        ('low', 'Low'),
        ('moderate', 'Moderate'),
        ('high', 'High'),
        ('intense', 'Intense'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workouts')
    workout_type = models.CharField(max_length=20, choices=WORKOUT_TYPES)
    duration_minutes = models.IntegerField(help_text="Duration in minutes")
    intensity = models.CharField(max_length=10, choices=INTENSITY_LEVELS)
    calories_burned = models.IntegerField(help_text="Estimated calories burned", null=True, blank=True)
    date = models.DateField(default=date.today)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        """Auto-calculate calories burned before saving"""
        if not self.calories_burned:
            self.calories_burned = self.calculate_calories_burned()
        super().save(*args, **kwargs)
    
    def calculate_calories_burned(self):
        """Automatic estimation of calories burned per session"""
        # Base calories per minute for different intensities
        intensity_multipliers = {
            'low': 5,
            'moderate': 8,
            'high': 11,
            'intense': 14,
        }
        
        type_multipliers = {
            'running': 1.2,
            'gym': 1.0,
            'cycling': 0.9,
            'swimming': 1.1,
            'home': 0.8,
            'yoga': 0.6,
            'other': 0.8,
        }
        
        base_calories = self.duration_minutes * intensity_multipliers.get(self.intensity, 8)
        calories = base_calories * type_multipliers.get(self.workout_type, 1.0)
        
        return int(calories)
    
    def __str__(self):
        return f"{self.user.username} - {self.workout_type} - {self.date}"