"""
Registration verification utilities for healthcare professionals
GMC, NMC, and HCPC registration number verification
"""
import requests
import re
from django.conf import settings
from django.utils import timezone


def get_registration_body_url(registration_body, registration_number=None, first_name=None, last_name=None):
    """
    Get the URL to check registration on the official register
    """
    if registration_body == 'GMC':
        # GMC register: https://www.gmc-uk.org/registration-and-licensing/our-registers
        return "https://www.gmc-uk.org/registration-and-licensing/our-registers"
    
    elif registration_body == 'NMC':
        # NMC register: https://www.nmc.org.uk/registration/search-the-register/
        return "https://www.nmc.org.uk/registration/search-the-register/"
    
    elif registration_body == 'HCPC':
        # HCPC register: https://www.hcpc-uk.org/check-the-register/
        return "https://www.hcpc-uk.org/check-the-register/"
    
    return None


def verify_registration_number(registration_body, registration_number, first_name=None, last_name=None, title=None):
    """
    Attempt to verify a registration number against the professional body
    Note: This is a basic implementation. Full verification may require API access
    or web scraping, which may have legal/ToS restrictions.
    
    Args:
        registration_body: The registration body (GMC, NMC, HCPC, etc.)
        registration_number: The registration number to verify
        first_name: Optional first name of the clinician
        last_name: Optional last name of the clinician
        title: Optional title/profession of the clinician (e.g., 'physiotherapist')
    
    Returns:
        dict with keys: 'verified', 'message', 'register_url'
    """
    if not registration_body or not registration_number:
        return {
            'verified': False,
            'message': 'Registration body and number required',
            'register_url': None
        }
    
    registration_number = registration_number.strip().upper()
    
    # Basic format validation
    if registration_body == 'GMC':
        # GMC numbers are typically 7-8 digits
        if not re.match(r'^\d{7,8}$', registration_number):
            return {
                'verified': False,
                'message': 'GMC registration numbers should be 7-8 digits',
                'register_url': get_registration_body_url(registration_body, registration_number, first_name, last_name)
            }
    
    elif registration_body == 'NMC':
        # NMC numbers are typically 8 digits (PIN)
        if not re.match(r'^\d{8}$', registration_number):
            return {
                'verified': False,
                'message': 'NMC registration numbers (PIN) should be 8 digits',
                'register_url': get_registration_body_url(registration_body, registration_number, first_name, last_name)
            }
    
    elif registration_body == 'HCPC':
        # HCPC numbers vary by profession
        # For physiotherapists: starts with PH followed by digits
        if title and title.lower() == 'physiotherapist':
            if not re.match(r'^PH\d+$', registration_number):
                return {
                    'verified': False,
                    'message': 'HCPC physiotherapist registration numbers should start with "PH" followed by digits (e.g., PH12345)',
                    'register_url': get_registration_body_url(registration_body, registration_number, first_name, last_name)
                }
        # For other HCPC professions, check minimum length
        elif len(registration_number) < 4:
            return {
                'verified': False,
                'message': 'HCPC registration numbers should be at least 4 characters',
                'register_url': get_registration_body_url(registration_body, registration_number, first_name, last_name)
            }
    
    # Get register URL for manual verification
    register_url = get_registration_body_url(registration_body, registration_number, first_name, last_name)
    
    # Note: Full automated verification would require:
    # 1. API access (if available from the professional bodies)
    # 2. Web scraping (may violate ToS)
    # 3. Third-party verification services
    
    # For now, return format-validated result with link to manual verification
    return {
        'verified': None,  # None means format is valid but not automatically verified
        'message': f'Format appears valid. Please verify on the official {registration_body} register.',
        'register_url': register_url,
        'format_valid': True
    }


def get_registration_body_name(registration_body):
    """Get the full name of the registration body"""
    names = {
        'GMC': 'General Medical Council',
        'NMC': 'Nursing and Midwifery Council',
        'HCPC': 'Health and Care Professions Council',
        'other': 'Other Registration Body'
    }
    return names.get(registration_body, 'Unknown')

