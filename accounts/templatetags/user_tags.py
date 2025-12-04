from django import template

register = template.Library()


@register.filter
def is_clinician(user):
    """Check if a user is a clinician"""
    if not user or not user.is_authenticated:
        return False
    # Use hasattr to safely check OneToOneField existence
    return hasattr(user, 'clinician_profile')

