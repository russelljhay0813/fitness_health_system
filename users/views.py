from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from .models import CustomUser, UserProfile
from .forms import CustomUserCreationForm, UserProfileForm
from django.contrib.auth.views import LoginView

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create user profile
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    
    def get_success_url(self):
        return reverse_lazy('dashboard')

@login_required
def profile_view(request):
    if request.method == 'POST':
        profile_form = UserProfileForm(request.POST, instance=request.user.profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        profile_form = UserProfileForm(instance=request.user.profile)
    
    context = {
        'profile_form': profile_form,
        'user': request.user,
    }
    return render(request, 'users/profile.html', context)

class AdminUserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'users/admin_users.html'
    context_object_name = 'users'
    
    def test_func(self):
        return self.request.user.is_admin_user()
    
    def get_queryset(self):
        return CustomUser.objects.all().order_by('-date_joined')

@login_required
def admin_toggle_user_status(request, user_id):
    if not request.user.is_admin_user():
        messages.error(request, 'You do not have permission to do this!')
        return redirect('dashboard')
    
    user = CustomUser.objects.get(id=user_id)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f'User {user.username} status updated!')
    return redirect('admin_users')

def logout_view(request):
    logout(request)
    return redirect('login')