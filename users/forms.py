from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-input'}))
    height = forms.FloatField(required=True, help_text="Height in centimeters", 
                              widget=forms.NumberInput(attrs={'class': 'form-input', 'step': '0.1'}))
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'height', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input'}),
        }
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.height = self.cleaned_data['height']
        if commit:
            user.save()
        return user

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['weight_goal', 'daily_calorie_goal', 'workout_goal_weekly']
        widgets = {
            'weight_goal': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'daily_calorie_goal': forms.NumberInput(attrs={'class': 'form-control'}),
            'workout_goal_weekly': forms.NumberInput(attrs={'class': 'form-control'}),
        }