from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from .models import UserProfile


class CustomLoginView(LoginView):
    """Custom login view with profile safety checks"""
    template_name = 'registration/login.html'
    
    def form_valid(self, form):
        """Override to ensure user has a profile"""
        # Authenticate and login the user
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        
        if user is not None:
            # Ensure user has a profile
            if not hasattr(user, 'profile'):
                try:
                    UserProfile.objects.get_or_create(user=user)
                except Exception:
                    # If profile creation fails, log but continue
                    pass
            
            login(self.request, user)
            
            # Determine redirect based on user type
            if hasattr(user, 'clinician_profile'):
                return redirect('clinicians:dashboard')
            else:
                return redirect('health_records:dashboard')
        
        return super().form_valid(form)


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ensure profile is created
            UserProfile.objects.get_or_create(user=user)
            # Automatically log in the user after registration
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to ShareMyCare.')
            return redirect('health_records:dashboard')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})
