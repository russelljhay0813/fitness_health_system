from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('admin/users/', views.AdminUserListView.as_view(), name='admin_users'),
    path('admin/toggle/<int:user_id>/', views.admin_toggle_user_status, name='toggle_user'),
]