from django.db import models
from django.contrib.auth import get_user_model
from datetime import date

User = get_user_model()

class Meal(models.Model):
    MEAL_TYPES = (
        ('breakfast', 'Breakfast'),
        ('lunch', 'Lunch'),
        ('dinner', 'Dinner'),
        ('snack', 'Snack'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='meals')
    meal_type = models.CharField(max_length=20, choices=MEAL_TYPES)
    food_name = models.CharField(max_length=200)
    calories = models.IntegerField(help_text="Calorie value")
    protein = models.FloatField(help_text="Protein in grams", default=0)
    carbs = models.FloatField(help_text="Carbohydrates in grams", default=0)
    fat = models.FloatField(help_text="Fat in grams", default=0)
    date = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.food_name} - {self.date}"

class Nutrition(models.Model):
    """Nutrition class tracks dietary records and calculates balances"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='nutrition_records')
    date = models.DateField(default=date.today)
    total_calories_intake = models.IntegerField(default=0)
    total_protein = models.FloatField(default=0)
    total_carbs = models.FloatField(default=0)
    total_fat = models.FloatField(default=0)
    
    class Meta:
        # Ensure one record per user per day
        unique_together = ['user', 'date']
    
    def update_totals(self):
        """Update daily totals from meals"""
        meals = Meal.objects.filter(user=self.user, date=self.date)
        self.total_calories_intake = sum(meal.calories for meal in meals)
        self.total_protein = sum(meal.protein for meal in meals)
        self.total_carbs = sum(meal.carbs for meal in meals)
        self.total_fat = sum(meal.fat for meal in meals)
        self.save()
    
    def calculate_net_calories(self, calories_burned):
        """Calculate net calorie balance"""
        return self.total_calories_intake - calories_burned
    
    def get_surplus_deficit_status(self, calories_burned, calorie_goal):
        """Daily surplus/deficit status indicator"""
        net = self.calculate_net_calories(calories_burned)
        if net < 0:
            return "Deficit", abs(net)
        elif net > 0:
            return "Surplus", net
        else:
            return "Maintenance", 0
    
    def __str__(self):
        return f"{self.user.username} - Nutrition - {self.date}"