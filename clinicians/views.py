from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Clinician, ClinicianInvitation, PatientClinicianAccess, ObjectiveMeasures
from .forms import ClinicianForm, ClinicianInvitationForm, ObjectiveMeasuresForm
from health_records.models import Assessment
from health_records.forms import PractitionerAssessmentForm


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
            
            # Handle free text inputs - if dropdown value is 'free_text', use the free text input
            rom_power_fields = [
                'shoulder_rom_left', 'shoulder_rom_right', 'elbow_rom_left', 'elbow_rom_right',
                'hip_rom_left', 'hip_rom_right', 'knee_rom_left', 'knee_rom_right',
                'ankle_rom_left', 'ankle_rom_right', 'wrist_rom_left', 'wrist_rom_right',
                'hand_rom_left', 'hand_rom_right', 'foot_rom_left', 'foot_rom_right',
                'cervical_rom', 'thoracic_rom', 'lumbar_rom',
                'shoulder_power_left', 'shoulder_power_right', 'elbow_power_left', 'elbow_power_right',
                'hip_power_left', 'hip_power_right', 'knee_power_left', 'knee_power_right',
                'ankle_power_left', 'ankle_power_right', 'wrist_power_left', 'wrist_power_right',
                'grip_power_left', 'grip_power_right', 'core_power'
            ]
            
            for field_name in rom_power_fields:
                field_value = getattr(objective_measures, field_name, None)
                if field_value == 'free_text':
                    # Get free text value from POST
                    free_text_key = f'{field_name}_free'
                    free_text_value = request.POST.get(free_text_key, '').strip()
                    if free_text_value:
                        setattr(objective_measures, field_name, free_text_value)
                    else:
                        setattr(objective_measures, field_name, 'normal')
                elif not field_value:
                    # Set default to 'normal' for empty fields
                    setattr(objective_measures, field_name, 'normal')
            
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
            
            # Handle free text inputs - if dropdown value is 'free_text', use the free text input
            rom_power_fields = [
                'shoulder_rom_left', 'shoulder_rom_right', 'elbow_rom_left', 'elbow_rom_right',
                'hip_rom_left', 'hip_rom_right', 'knee_rom_left', 'knee_rom_right',
                'ankle_rom_left', 'ankle_rom_right', 'wrist_rom_left', 'wrist_rom_right',
                'hand_rom_left', 'hand_rom_right', 'foot_rom_left', 'foot_rom_right',
                'cervical_rom', 'thoracic_rom', 'lumbar_rom',
                'shoulder_power_left', 'shoulder_power_right', 'elbow_power_left', 'elbow_power_right',
                'hip_power_left', 'hip_power_right', 'knee_power_left', 'knee_power_right',
                'ankle_power_left', 'ankle_power_right', 'wrist_power_left', 'wrist_power_right',
                'grip_power_left', 'grip_power_right', 'core_power'
            ]
            
            for field_name in rom_power_fields:
                field_value = getattr(objective_measures, field_name, None)
                if field_value == 'free_text':
                    # Get free text value from POST
                    free_text_key = f'{field_name}_free'
                    free_text_value = request.POST.get(free_text_key, '').strip()
                    if free_text_value:
                        setattr(objective_measures, field_name, free_text_value)
                    else:
                        setattr(objective_measures, field_name, 'normal')
                elif not field_value:
                    # Set default to 'normal' for empty fields
                    setattr(objective_measures, field_name, 'normal')
            
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
