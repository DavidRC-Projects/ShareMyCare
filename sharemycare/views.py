from django.shortcuts import render


def handler404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)


def handler500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)


def security(request):
    """Security page"""
    return render(request, 'pages/security.html')


def support(request):
    """Support page"""
    return render(request, 'pages/support.html')


def help_center(request):
    """Help Centre page"""
    return render(request, 'pages/help_center.html')


def contact(request):
    """Contact page"""
    return render(request, 'pages/contact.html')


def legal(request):
    """Legal page"""
    return render(request, 'pages/legal.html')


def privacy(request):
    """Privacy Policy page"""
    return render(request, 'pages/privacy.html')


def terms(request):
    """Terms of Service page"""
    return render(request, 'pages/terms.html')
