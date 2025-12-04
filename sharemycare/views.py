"""
Custom error handlers for ShareMyCare
"""
from django.shortcuts import render
from django.http import HttpResponseNotFound, HttpResponseServerError


def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)

