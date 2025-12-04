def user_context(request):
    """Add user context to all templates"""
    context = {}
    if request.user.is_authenticated:
        # Check if user is a clinician using hasattr to safely check OneToOneField
        context['is_clinician'] = hasattr(request.user, 'clinician_profile')
    else:
        context['is_clinician'] = False
    return context

