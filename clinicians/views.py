from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import models
import json
from .models import Clinician, ClinicianInvitation, PatientClinicianAccess, ObjectiveMeasures
from .forms import ClinicianForm, ClinicianInvitationForm, ObjectiveMeasuresForm
from health_records.models import Assessment
from health_records.forms import PractitionerAssessmentForm


def aggregate_movement_fields(request, objective_measures):
    """
    Aggregate specific movement fields from POST data into generic model fields.
    The template uses specific field names (e.g., ankle_dorsiflexion_rom_left) 
    but the model has generic fields (e.g., ankle_rom_left).
    Stores data as JSON strings in the model fields.
    """
    import re
    
    # Define joints with left/right sides
    bilateral_joints = {
        'ankle': 'ankle',
        'knee': 'knee',
        'hip': 'hip',
        'shoulder': 'shoulder',
        'elbow': 'elbow',
        'wrist': 'wrist',
    }
    
    # Process bilateral joints (with left/right)
    for joint_name, field_prefix in bilateral_joints.items():
        rom_left_data = {}
        rom_right_data = {}
        power_left_data = {}
        power_right_data = {}
        
        # Pattern to match: {joint}_{movement}_rom_{side} or {joint}_{movement}_strength_{side}
        pattern_rom = re.compile(rf'^{joint_name}_(.+)_rom_(left|right)$')
        pattern_strength = re.compile(rf'^{joint_name}_(.+)_strength_(left|right)$')
        
        # Process all POST fields for this joint
        for key, value in request.POST.items():
            if not value or value.strip() == '':
                continue
                
            # Match ROM fields
            rom_match = pattern_rom.match(key)
            if rom_match:
                movement = rom_match.group(1)
                side = rom_match.group(2)
                if side == 'left':
                    rom_left_data[movement] = value
                else:
                    rom_right_data[movement] = value
                continue
            
            # Match strength/power fields
            strength_match = pattern_strength.match(key)
            if strength_match:
                movement = strength_match.group(1)
                side = strength_match.group(2)
                if side == 'left':
                    power_left_data[movement] = value
                else:
                    power_right_data[movement] = value
                continue
        
        # Store aggregated data as JSON strings
        if rom_left_data:
            setattr(objective_measures, f'{field_prefix}_rom_left', json.dumps(rom_left_data))
        if rom_right_data:
            setattr(objective_measures, f'{field_prefix}_rom_right', json.dumps(rom_right_data))
        if power_left_data:
            setattr(objective_measures, f'{field_prefix}_power_left', json.dumps(power_left_data))
        if power_right_data:
            setattr(objective_measures, f'{field_prefix}_power_right', json.dumps(power_right_data))
    
    # Process spine joints (cervical and lumbar) - no left/right
    for joint_name, field_prefix in [('cervical', 'cervical'), ('lumbar', 'lumbar')]:
        pattern_rom_spine = re.compile(rf'^{joint_name}_(.+)_rom$')
        pattern_strength_spine = re.compile(rf'^{joint_name}_(.+)_strength$')
        
        rom_data = {}
        power_data = {}
        
        for key, value in request.POST.items():
            if not value or value.strip() == '':
                continue
                
            rom_match = pattern_rom_spine.match(key)
            if rom_match:
                movement = rom_match.group(1)
                rom_data[movement] = value
                continue
            
            strength_match = pattern_strength_spine.match(key)
            if strength_match:
                movement = strength_match.group(1)
                power_data[movement] = value
                continue
        
        # Store ROM data
        if rom_data:
            setattr(objective_measures, f'{field_prefix}_rom', json.dumps(rom_data))
        
        # Store power data - lumbar uses core_power, cervical has no power field in model
        if power_data:
            if joint_name == 'lumbar':
                setattr(objective_measures, 'core_power', json.dumps(power_data))
            # Note: cervical power is not stored as there's no cervical_power field in the model


def practitioner_login(request):
    """Practitioner login view"""
    if request.user.is_authenticated:
        # Check if user is a clinician
        if hasattr(request.user, 'clinician_profile'):
            return redirect('clinicians:dashboard')
        else:
            # Regular user, redirect to patient dashboard
            return redirect('health_records:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Check if user is a clinician
                if hasattr(user, 'clinician_profile'):
                    try:
                        clinician = user.clinician_profile
                        # Ensure practitioner code exists
                        if not clinician.practitioner_code:
                            clinician.save()  # This will generate the code via the save() method
                        login(request, user)
                        messages.success(request, f'Welcome, {clinician.full_name}!')
                        return redirect('clinicians:dashboard')
                    except Exception as e:
                        import traceback
                        messages.error(request, f'An error occurred during login. Please try again.')
                        # Log the error for debugging
                        print(f"Error in practitioner_login: {e}")
                        print(traceback.format_exc())
                else:
                    messages.error(request, 'This login is for practitioners only. Please use the regular sign in.')
            else:
                messages.error(request, 'Invalid username or password.')
    
    # Render the login form (for both GET and POST with errors)
    return render(request, 'clinicians/practitioner_login.html')


@login_required
def practitioner_dashboard(request):
    """Practitioner dashboard view"""
    if not hasattr(request.user, 'clinician_profile'):
        messages.error(request, 'You must be a registered clinician to access this page.')
        return redirect('health_records:dashboard')
    
    clinician = request.user.clinician_profile
    
    # Get all patients this clinician has access to
    from clinicians.models import PatientClinicianAccess
    from health_records.models import Assessment
    
    patient_accesses = PatientClinicianAccess.objects.filter(
        clinician=clinician,
        is_active=True
    ).select_related('patient')
    
    # Get assessments for each patient that need objective measures
    patients_with_assessments = []
    for access in patient_accesses:
        patient = access.patient
        assessments = Assessment.objects.filter(user=patient).order_by('-symptom_date', '-created_at')
        patients_with_assessments.append({
            'patient': patient,
            'access': access,
            'assessments': assessments,
        })
    
    # Debug: Log the data being passed to template
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"Practitioner dashboard - clinician: {clinician.id}, patient_accesses: {patient_accesses.count()}, patients_with_assessments: {len(patients_with_assessments)}")
    
    context = {
        'clinician': clinician,
        'patient_accesses': patient_accesses,
        'patients_with_assessments': patients_with_assessments,
    }
    return render(request, 'clinicians/dashboard.html', context)


@login_required
def clients_list(request):
    """View all clients (patients) that the clinician has access to"""
    if not hasattr(request.user, 'clinician_profile'):
        messages.error(request, 'You must be a registered clinician to access this page.')
        return redirect('health_records:dashboard')
    
    clinician = request.user.clinician_profile
    
    # Get all active patient accesses
    patient_accesses = PatientClinicianAccess.objects.filter(
        clinician=clinician,
        is_active=True
    ).select_related('patient').prefetch_related('patient__assessments', 'patient__medications', 'patient__conditions', 'patient__allergies')
    
    # Search functionality
    search_query = request.GET.get('search', '').strip()
    if search_query:
        patient_accesses = patient_accesses.filter(
            models.Q(patient__username__icontains=search_query) |
            models.Q(patient__first_name__icontains=search_query) |
            models.Q(patient__last_name__icontains=search_query) |
            models.Q(patient__email__icontains=search_query)
        )
    
    # Prepare client data with stats
    clients_data = []
    from health_records.models import Assessment
    from django.utils import timezone
    from datetime import timedelta
    
    for access in patient_accesses:
        patient = access.patient
        assessments = Assessment.objects.filter(user=patient)
        
        # Calculate stats
        total_assessments = assessments.count()
        recent_assessment = assessments.order_by('-assessment_date', '-created_at').first()
        last_visit = recent_assessment.assessment_date if recent_assessment and recent_assessment.assessment_date else None
        
        # Count other records
        medications_count = patient.medications.filter(is_active=True).count()
        conditions_count = patient.conditions.filter(status='active').count()
        allergies_count = patient.allergies.count()
        
        # Check if patient has recent activity (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        has_recent_activity = assessments.filter(
            models.Q(assessment_date__gte=thirty_days_ago.date()) |
            models.Q(created_at__gte=thirty_days_ago)
        ).exists()
        
        clients_data.append({
            'patient': patient,
            'access': access,
            'total_assessments': total_assessments,
            'last_visit': last_visit,
            'medications_count': medications_count,
            'conditions_count': conditions_count,
            'allergies_count': allergies_count,
            'has_recent_activity': has_recent_activity,
            'recent_assessment': recent_assessment,
        })
    
    # Sort by last visit (most recent first) or by name if no visits
    from datetime import date
    clients_data.sort(key=lambda x: (
        x['last_visit'] if x['last_visit'] else date.min,
        (x['patient'].get_full_name() or x['patient'].username).lower()
    ), reverse=True)
    
    context = {
        'clinician': clinician,
        'clients_data': clients_data,
        'search_query': search_query,
        'total_clients': len(clients_data),
    }
    return render(request, 'clinicians/clients_list.html', context)


@login_required
def client_detail(request, patient_id):
    """View detailed information about a specific client"""
    if not hasattr(request.user, 'clinician_profile'):
        messages.error(request, 'You must be a registered clinician to access this page.')
        return redirect('health_records:dashboard')
    
    clinician = request.user.clinician_profile
    patient = get_object_or_404(User, pk=patient_id)
    
    # Check if clinician has access to this patient
    access = PatientClinicianAccess.objects.filter(
        patient=patient,
        clinician=clinician,
        is_active=True
    ).first()
    
    if not access:
        messages.error(request, 'You do not have access to this patient\'s records.')
        return redirect('clinicians:clients_list')
    
    # Get all patient data
    from health_records.models import Assessment, Medication, Condition, Allergy, WorkHistory
    
    assessments = Assessment.objects.filter(user=patient).order_by('-assessment_date', '-created_at')
    medications = Medication.objects.filter(user=patient).order_by('-is_active', '-start_date')
    conditions = Condition.objects.filter(user=patient).order_by('-diagnosis_date')
    allergies = Allergy.objects.filter(user=patient).order_by('-severity', '-date_identified')
    work_history = WorkHistory.objects.filter(user=patient).order_by('-is_current', '-start_date')
    
    # Get patient profile
    try:
        profile = patient.profile
    except:
        profile = None
    
    # Get recent assessments count
    from django.utils import timezone
    from datetime import timedelta
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_assessments = assessments.filter(
        models.Q(assessment_date__gte=thirty_days_ago.date()) | 
        models.Q(created_at__gte=thirty_days_ago)
    )
    
    context = {
        'clinician': clinician,
        'patient': patient,
        'access': access,
        'profile': profile,
        'assessments': assessments,
        'medications': medications,
        'conditions': conditions,
        'allergies': allergies,
        'work_history': work_history,
        'recent_assessments_count': recent_assessments.count(),
        'total_assessments': assessments.count(),
    }
    return render(request, 'clinicians/client_detail.html', context)


@login_required
def edit_clinician_profile(request):
    """Edit clinician profile"""
    if not hasattr(request.user, 'clinician_profile'):
        messages.error(request, 'You must be a registered clinician to access this page.')
        return redirect('health_records:dashboard')
    
    clinician = request.user.clinician_profile
    
    if request.method == 'POST':
        form = ClinicianForm(request.POST, instance=clinician)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('clinicians:dashboard')
    else:
        form = ClinicianForm(instance=clinician)
    
    return render(request, 'clinicians/edit_profile.html', {'form': form, 'clinician': clinician})


@login_required
def delete_clinician_profile(request):
    """Delete clinician profile (and associated user account)"""
    if not hasattr(request.user, 'clinician_profile'):
        messages.error(request, 'You must be a registered clinician to access this page.')
        return redirect('health_records:dashboard')
    
    clinician = request.user.clinician_profile
    
    if request.method == 'POST':
        user = request.user
        # Delete the clinician profile first
        clinician.delete()
        # Then delete the user account
        user.delete()
        messages.success(request, 'Your account has been deleted successfully.')
        return redirect('health_records:home')
    
    return render(request, 'clinicians/delete_confirm.html', {'clinician': clinician})


def clinician_signup(request, token):
    """Clinician signup via invitation token"""
    invitation = get_object_or_404(ClinicianInvitation, token=token)
    
    if not invitation.is_valid():
        messages.error(request, 'This invitation has expired or has already been used.')
        return redirect('health_records:home')
    
    # Initialize form data for template
    form_data = {}
    form_errors = {}
    
    if request.method == 'POST':
        # Create user account
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        # Preserve form data for re-rendering
        form_data = {
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
        }
        
        # Validate inputs
        has_errors = False
        
        if not username:
            form_errors['username'] = 'Username is required.'
            has_errors = True
        elif User.objects.filter(username=username).exists():
            form_errors['username'] = 'Username already exists.'
            has_errors = True
        
        if not password1:
            form_errors['password1'] = 'Password is required.'
            has_errors = True
        elif len(password1) < 8:
            form_errors['password1'] = 'Password must be at least 8 characters long.'
            has_errors = True
        
        if password1 != password2:
            form_errors['password2'] = 'Passwords do not match.'
            has_errors = True
        
        if has_errors:
            # Re-render template with form data and errors
            return render(request, 'clinicians/signup.html', {
                'invitation': invitation,
                'form_data': form_data,
                'form_errors': form_errors
            })
        
        # All validation passed - create user
        user = User.objects.create_user(
            username=username,
            email=invitation.email,
            password=password1
        )
        
        # Create clinician profile
        clinician = Clinician.objects.create(
            user=user,
            email=invitation.email,
            first_name=first_name or invitation.first_name or '',
            last_name=last_name or invitation.last_name or '',
        )
        
        # Create access relationship
        PatientClinicianAccess.objects.create(
            patient=invitation.patient,
            clinician=clinician,
            access_granted_by=invitation.patient,
            access_level='full',
            is_active=True
        )
        
        # Mark invitation as accepted
        invitation.is_accepted = True
        invitation.save()
        
        # Log in the new clinician
        login(request, user)
        messages.success(
            request, 
            f'Welcome! You now have access to {invitation.patient.username}\'s records. '
            f'Your practitioner code is: {clinician.practitioner_code}'
        )
        return redirect('clinicians:dashboard')
    
    return render(request, 'clinicians/signup.html', {
        'invitation': invitation,
        'form_data': form_data,
        'form_errors': form_errors
    })


@login_required
def add_objective_measures(request, assessment_pk):
    """Add objective measures to an assessment"""
    if not hasattr(request.user, 'clinician_profile'):
        messages.error(request, 'You must be a registered clinician to access this page.')
        return redirect('health_records:dashboard')
    
    from health_records.models import Assessment
    clinician = request.user.clinician_profile
    assessment = get_object_or_404(Assessment, pk=assessment_pk)
    
    # Check if clinician has access to this patient
    has_access = PatientClinicianAccess.objects.filter(
        patient=assessment.user,
        clinician=clinician,
        is_active=True
    ).exists()
    
    if not has_access:
        messages.error(request, 'You do not have access to this patient\'s records.')
        return redirect('clinicians:dashboard')
    
    # Check if objective measures already exist
    if hasattr(assessment, 'objective_measures'):
        return redirect('clinicians:edit_objective_measures', pk=assessment.objective_measures.pk)
    
    if request.method == 'POST':
        form = ObjectiveMeasuresForm(request.POST, assessment=assessment)
        if form.is_valid():
            objective_measures = form.save(commit=False)
            objective_measures.assessment = assessment
            objective_measures.clinician = clinician
            
            # Aggregate specific movement fields from template into generic model fields
            aggregate_movement_fields(request, objective_measures)
            
            objective_measures.save()
            messages.success(request, 'Objective measures added successfully!')
            return redirect('clinicians:dashboard')
    else:
        form = ObjectiveMeasuresForm(assessment=assessment)
    
    return render(request, 'clinicians/objective_measures_form.html', {
        'form': form,
        'assessment': assessment,
        'patient': assessment.user
    })


@login_required
def edit_objective_measures(request, pk):
    """Edit objective measures"""
    if not hasattr(request.user, 'clinician_profile'):
        messages.error(request, 'You must be a registered clinician to access this page.')
        return redirect('health_records:dashboard')
    
    clinician = request.user.clinician_profile
    objective_measures = get_object_or_404(ObjectiveMeasures, pk=pk, clinician=clinician)
    
    if request.method == 'POST':
        form = ObjectiveMeasuresForm(request.POST, instance=objective_measures, assessment=objective_measures.assessment)
        if form.is_valid():
            objective_measures = form.save(commit=False)
            
            # Aggregate specific movement fields from template into generic model fields
            aggregate_movement_fields(request, objective_measures)
            
            objective_measures.save()
            messages.success(request, 'Objective measures updated successfully!')
            return redirect('clinicians:dashboard')
    else:
        form = ObjectiveMeasuresForm(instance=objective_measures, assessment=objective_measures.assessment)
    
    return render(request, 'clinicians/objective_measures_form.html', {
        'form': form,
        'assessment': objective_measures.assessment,
        'patient': objective_measures.assessment.user,
        'objective_measures': objective_measures
    })


@login_required
def create_assessment(request, patient_id):
    """Create a new assessment for a patient - different forms based on practitioner type"""
    if not hasattr(request.user, 'clinician_profile'):
        messages.error(request, 'You must be a registered clinician to access this page.')
        return redirect('health_records:dashboard')
    
    clinician = request.user.clinician_profile
    patient = get_object_or_404(User, pk=patient_id)
    
    # Check if clinician has access to this patient
    has_access = PatientClinicianAccess.objects.filter(
        patient=patient,
        clinician=clinician,
        is_active=True
    ).exists()
    
    if not has_access:
        messages.error(request, 'You do not have access to this patient\'s records.')
        return redirect('clinicians:dashboard')
    
    # Determine assessment type based on practitioner title
    is_physiotherapist = clinician.title == 'physiotherapist'
    
    if request.method == 'POST':
        from health_records.forms import PractitionerAssessmentForm
        form = PractitionerAssessmentForm(request.POST, request.FILES, clinician=clinician)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.user = patient
            assessment.clinician = clinician
            # Auto-set assessment_type based on practitioner title
            if is_physiotherapist:
                assessment.assessment_type = 'physiotherapy'
            # Set completed_at to now if not provided
            if not assessment.completed_at:
                assessment.completed_at = timezone.now()
            assessment.save()
            
            # Check if user wants to add objective measures
            if is_physiotherapist and request.POST.get('add_objective_measures'):
                messages.success(request, 'Assessment saved. Now add detailed objective measures.')
                return redirect('clinicians:add_objective_measures', assessment_pk=assessment.pk)
            
            messages.success(request, 'Assessment created successfully!')
            
            # For physiotherapists, redirect to dashboard (they can add objective measures later)
            if is_physiotherapist:
                return redirect('clinicians:dashboard')
            return redirect('clinicians:dashboard')
    else:
        from health_records.forms import PractitionerAssessmentForm
        form = PractitionerAssessmentForm(clinician=clinician)
        # Pre-fill completed_at with current date/time
        form.fields['completed_at'].initial = timezone.now()
        # Pre-set assessment_type for physiotherapists
        if is_physiotherapist:
            form.fields['assessment_type'].initial = 'physiotherapy'
    
    return render(request, 'clinicians/create_assessment.html', {
        'form': form,
        'patient': patient,
        'clinician': clinician,
        'is_physiotherapist': is_physiotherapist
    })
