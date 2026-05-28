from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, UpdateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView
from .models import CustomUser, UserProfile
from .forms import CustomUserCreationForm, UserProfileForm
from workouts.models import Workout
from nutrition.models import Meal
from analytics.models import HealthData, FitnessGoal
from datetime import date, timedelta
from django.db.models import Sum, Count, Avg

# ========== REGISTER VIEW ==========
def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            # Log the user in
            auth_login(request, user)
            messages.success(request, 'Registration successful! Welcome to Fitness Health Analytics!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

# ========== LOGIN VIEW ==========
class CustomLoginView(LoginView):
    """Custom login view with redirect"""
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('dashboard')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

# ========== LOGOUT VIEW ==========
def logout_view(request):
    """User logout view"""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('login')

# ========== PROFILE VIEW ==========
@login_required
def profile_view(request):
    """Profile page with user statistics and edit form"""
    
    # Get or create profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Handle form submission
    if request.method == 'POST':
        # Update user basic info
        request.user.email = request.POST.get('email', request.user.email)
        request.user.first_name = request.POST.get('first_name', request.user.first_name)
        request.user.last_name = request.POST.get('last_name', request.user.last_name)
        
        # Update height if provided
        if request.POST.get('height'):
            try:
                request.user.height = float(request.POST.get('height'))
            except ValueError:
                pass
        
        request.user.save()
        
        # Update profile
        if request.POST.get('weight_goal'):
            try:
                profile.weight_goal = float(request.POST.get('weight_goal'))
            except ValueError:
                pass
                
        if request.POST.get('daily_calorie_goal'):
            try:
                profile.daily_calorie_goal = int(request.POST.get('daily_calorie_goal'))
            except ValueError:
                pass
                
        if request.POST.get('workout_goal_weekly'):
            try:
                profile.workout_goal_weekly = int(request.POST.get('workout_goal_weekly'))
            except ValueError:
                pass
        
        profile.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('profile')
    
    # Get statistics
    total_workouts = Workout.objects.filter(user=request.user).count()
    total_meals = Meal.objects.filter(user=request.user).count()
    total_weight_entries = HealthData.objects.filter(user=request.user).count()
    
    # Get last 7 days activity
    week_ago = date.today() - timedelta(days=7)
    weekly_workouts = Workout.objects.filter(user=request.user, date__gte=week_ago).count()
    
    # Get latest weight
    latest_weight = HealthData.objects.filter(user=request.user).order_by('-date').first()
    
    # Calculate BMI
    bmi = None
    bmi_category = None
    if latest_weight and request.user.height:
        height_m = request.user.height / 100
        bmi = round(latest_weight.weight_kg / (height_m * height_m), 1)
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif bmi < 25:
            bmi_category = "Normal"
        elif bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"
    
    # Get goals
    active_goals = FitnessGoal.objects.filter(user=request.user).exclude(status='completed')
    completed_goals = FitnessGoal.objects.filter(user=request.user, status='completed').count()
    total_goals = FitnessGoal.objects.filter(user=request.user).count()
    
    # Calculate streak
    streak = 0
    workouts = Workout.objects.filter(user=request.user).order_by('-date')
    if workouts.exists():
        current_date = date.today()
        for i in range(30):
            check_date = current_date - timedelta(days=i)
            if workouts.filter(date=check_date).exists():
                streak += 1
            else:
                break
    
    context = {
        'profile': profile,
        'user': request.user,
        'total_workouts': total_workouts,
        'total_meals': total_meals,
        'total_weight_entries': total_weight_entries,
        'weekly_workouts': weekly_workouts,
        'latest_weight': latest_weight,
        'bmi': bmi,
        'bmi_category': bmi_category,
        'active_goals': active_goals,
        'completed_goals': completed_goals,
        'total_goals': total_goals,
        'streak': streak,
    }
    
    return render(request, 'users/profile.html', context)

# ========== ADMIN USER LIST VIEW ==========
class AdminUserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'users/admin_users.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def test_func(self):
        return self.request.user.is_admin_user()
    
    def get_queryset(self):
        return CustomUser.objects.all().order_by('-date_joined')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = CustomUser.objects.count()
        context['active_users'] = CustomUser.objects.filter(is_active=True).count()
        return context

# ========== ADMIN TOGGLE USER STATUS ==========
@login_required
def admin_toggle_user_status(request, user_id):
    """Admin view to enable/disable user accounts"""
    if not request.user.is_admin_user():
        messages.error(request, 'You do not have permission to do this!')
        return redirect('dashboard')
    
    try:
        user = CustomUser.objects.get(id=user_id)
        if user == request.user:
            messages.error(request, 'You cannot disable your own account!')
        else:
            user.is_active = not user.is_active
            user.save()
            status = "enabled" if user.is_active else "disabled"
            messages.success(request, f'User {user.username} has been {status}.')
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
    
    return redirect('admin_users')

# ========== SIMPLE LOGIN TEST (Optional) ==========
def simple_login(request):
    """Simple working login view as fallback"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'users/login.html')