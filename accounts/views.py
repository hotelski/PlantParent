from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, FormView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .forms import (
    UserRegistrationForm,
    UserLoginForm,
    UserProfileForm,
    PasswordChangeForm
)

class RegisterView(CreateView):
    # Use the custom registration form
    form_class = UserRegistrationForm
    # Template to render the form
    template_name = 'accounts/register.html'
    # Where to redirect after success
    success_url = reverse_lazy('products:home')

    def form_valid(self, form):
        # Log the user in automatically after successful registration
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

class LoginView(FormView):
    form_class = UserLoginForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('products:home')

    def form_valid(self, form):
        # Log in the user
        login(self.request, form.get_user())
        return super().form_valid(form)

def logout_view(request):
    # Log out the user and redirect to home page
    logout(request)
    return redirect('products:home')

@login_required
def profile_update(request):
    if request.method == 'POST':
        # Load form with submitted data and uploaded files
        form = UserProfileForm(
            request.POST, 
            request.FILES, 
            instance=request.user
        )
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Load form with current user data
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

class PasswordChangeView(LoginRequiredMixin, FormView):
    form_class = PasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('accounts:profile')

    def form_valid(self, form):
        # Update user's password and re-login
        user = self.request.user
        user.set_password(form.cleaned_data['new_password'])
        user.save()
        # Keep user logged in after password change
        login(self.request, user)
        return super().form_valid(form)