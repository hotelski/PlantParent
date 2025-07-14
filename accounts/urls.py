from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # URL for user registration page
    path('register/', views.RegisterView.as_view(), name='register'),
    # URL for login page
    path('login/', views.LoginView.as_view(), name='login'),
    # URL for logging out the user
    path('logout/', views.logout_view, name='logout'),
    # URL for updating user profile
    path('profile/', views.profile_update, name='profile'),
    # URL for changing the password
    path('password-change/', views.PasswordChangeView.as_view(), name='password_change'),
]