from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def home(request):
    """Homepage view"""
    return render(request, 'health_records/home.html')


@login_required
def dashboard(request):
    """User dashboard view"""
    return render(request, 'health_records/dashboard.html')
