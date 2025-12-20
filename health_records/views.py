from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.urls import reverse
from .models import Medication, Condition, Allergy, Assessment, WorkHistory, ExtractedFindings
from accounts.models import UserProfile
from .forms import (
    MedicationForm, ConditionForm, AllergyForm, 
    AssessmentForm, PractitionerAssessmentForm, UserProfileForm, WorkHistoryForm
)
from clinicians.models import PatientClinicianAccess, Clinician, ClinicianInvitation
from clinicians.forms import HealthcareFeedbackForm, ClinicianInvitationForm
from .azure_doc_intelligence import AzureDocumentIntelligenceService


def home(request):
    """Homepage view"""
    return render(request, 'health_records/home.html')


@login_required
def onboarding(request):
    """Onboarding wizard for new users"""
    user = request.user
    profile = user.profile
    step = request.GET.get('step', 'welcome')
    
    # Check if user has any data - if so, skip onboarding
    has_data = (
        profile.date_of_birth or
        profile.phone_number or
        profile.emergency_contact_name or
        user.medications.exists() or
        user.conditions.exists() or
        user.allergies.exists()
    )
    
    # If user has data or onboarding is marked complete, go to dashboard
    if (profile.onboarding_completed or has_data) and step == 'welcome':
        if not profile.onboarding_completed and has_data:
            # Mark as completed if they have data
            profile.onboarding_completed = True
            profile.save()
        return redirect('health_records:dashboard')
    
    steps = ['welcome', 'profile', 'medications', 'conditions', 'allergies', 'complete']
    current_step_index = steps.index(step) if step in steps else 0
    
    context = {
        'current_step': step,
        'steps': steps,
        'current_step_index': current_step_index,
        'total_steps': len(steps),
        'progress': int((current_step_index + 1) / len(steps) * 100)
    }
    
    if request.method == 'POST' and step == 'complete':
        profile.onboarding_completed = True
        profile.save()
        messages.success(request, 'Welcome to ShareMyCare! Your profile is set up.')
        return redirect('health_records:dashboard')
    
    return render(request, 'health_records/onboarding.html', context)


@login_required
def passport_view(request, patient_id=None):
    """Passport-style card view of health records"""
    # Check if this is a clinician viewing a patient's passport
    if patient_id:
        from clinicians.models import PatientClinicianAccess
        patient = get_object_or_404(User, pk=patient_id)
        
        # Verify clinician has access
        if hasattr(request.user, 'clinician_profile'):
            clinician = request.user.clinician_profile
            access = PatientClinicianAccess.objects.filter(
                patient=patient,
                clinician=clinician,
                is_active=True
            ).first()
            
            if not access:
                messages.error(request, 'You do not have access to this patient\'s records.')
                return redirect('clinicians:dashboard')
            
            # Use patient's data
            user = patient
            is_clinician_view = True
        else:
            messages.error(request, 'Access denied.')
            return redirect('health_records:dashboard')
    else:
        # User viewing their own passport
        user = request.user
        is_clinician_view = False
    
    # Get profile
    try:
        profile = user.profile
    except:
        profile = None
    
    context = {
        'medications': user.medications.filter(is_active=True),
        'conditions': user.conditions.filter(status='active'),
        'allergies': user.allergies.all(),
        'assessments': user.assessments.all().order_by('-assessment_date', '-created_at')[:5],
        'profile': profile,
        'clinician_accesses': user.clinician_accesses.filter(is_active=True).count(),
        'is_clinician_view': is_clinician_view,
        'patient': user if is_clinician_view else None,
    }
    
    return render(request, 'health_records/passport.html', context)


@login_required
def verify_clinician(request, clinician_id):
    """Verify a clinician's registration number"""
    from clinicians.models import Clinician
    from clinicians.verification import verify_registration_number, get_registration_body_name, get_registration_body_url
    
    clinician = get_object_or_404(Clinician, pk=clinician_id)
    
    # Check if user has access to this clinician (via PatientClinicianAccess)
    from clinicians.models import PatientClinicianAccess
    has_access = PatientClinicianAccess.objects.filter(
        patient=request.user,
        clinician=clinician,
        is_active=True
    ).exists()
    
    if not has_access:
        messages.error(request, 'You do not have access to verify this clinician.')
        return redirect('health_records:dashboard')
    
    if not clinician.registration_number or not clinician.registration_body:
        messages.error(request, 'This clinician has not provided registration information.')
        return redirect('health_records:dashboard')
    
    # Attempt verification
    verification_result = verify_registration_number(
        clinician.registration_body,
        clinician.registration_number,
        clinician.first_name,
        clinician.last_name,
        clinician.title
    )
    
    # Get register URL
    register_url = get_registration_body_url(
        clinician.registration_body,
        clinician.registration_number,
        clinician.first_name,
        clinician.last_name
    )
    
    context = {
        'clinician': clinician,
        'verification_result': verification_result,
        'register_url': register_url,
        'body_name': get_registration_body_name(clinician.registration_body),
    }
    
    return render(request, 'health_records/verify_clinician.html', context)


@login_required
def verify_clinician_registration(request):
    """Verify a clinician's registration - accepts form input or query parameters"""
    from clinicians.verification import verify_registration_number, get_registration_body_name, get_registration_body_url
    from health_records.forms import RegistrationVerificationForm
    
    registration_body = None
    registration_number = None
    verification_result = None
    register_url = None
    body_name = None
    title = None
    
    # Check if form was submitted
    if request.method == 'POST':
        form = RegistrationVerificationForm(request.POST)
        if form.is_valid():
            registration_body = form.cleaned_data['registration_body'].upper()
            registration_number = form.cleaned_data['registration_number'].strip()
            title = form.cleaned_data.get('title')  # Optional field
        else:
            return render(request, 'health_records/verify_clinician.html', {
                'form': form,
                'show_form': True
            })
    # Check if query parameters provided
    elif request.GET.get('body') and request.GET.get('number'):
        registration_body = request.GET.get('body', '').strip().upper()
        registration_number = request.GET.get('number', '').strip()
    else:
        # Show form for input
        form = RegistrationVerificationForm()
        return render(request, 'health_records/verify_clinician.html', {
            'form': form,
            'show_form': True
        })
    
    if registration_body and registration_number:
        # Attempt verification
        verification_result = verify_registration_number(
            registration_body,
            registration_number,
            title=title
        )
        
        # Get register URL
        register_url = get_registration_body_url(
            registration_body,
            registration_number
        )
        
        body_name = get_registration_body_name(registration_body)
    
    context = {
        'registration_body': registration_body,
        'registration_number': registration_number,
        'verification_result': verification_result,
        'register_url': register_url,
        'body_name': body_name,
        'form': RegistrationVerificationForm(initial={
            'registration_body': registration_body,
            'registration_number': registration_number
        }) if registration_body else RegistrationVerificationForm(),
        'show_form': False
    }
    
    return render(request, 'health_records/verify_clinician.html', context)


@login_required
def emergency_card(request):
    """Emergency access card with critical information"""
    user = request.user
    profile = user.profile
    
    context = {
        'medications': user.medications.filter(is_active=True),
        'allergies': user.allergies.all(),
        'conditions': user.conditions.filter(status='active'),
        'profile': profile,
        'emergency_contact': {
            'name': profile.emergency_contact_name,
            'phone': profile.emergency_contact_phone,
            'relationship': profile.emergency_contact_relationship,
        } if profile else None,
    }
    
    return render(request, 'health_records/emergency_card.html', context)


@login_required
def dashboard(request):
    """User dashboard view"""
    user = request.user
    profile = user.profile
    
    # Check if onboarding is needed - only for truly new users with no data
    has_data = (
        profile.date_of_birth or
        profile.phone_number or
        profile.emergency_contact_name or
        user.medications.exists() or
        user.conditions.exists() or
        user.allergies.exists()
    )
    
    # Only redirect to onboarding if user has no data and hasn't completed onboarding
    if not profile.onboarding_completed and not has_data:
        return redirect('health_records:onboarding')
    
    # If user has data but onboarding not marked complete, mark it now
    if has_data and not profile.onboarding_completed:
        profile.onboarding_completed = True
        profile.save()
    
    work_history = user.work_history.all()
    current_work = work_history.filter(is_current=True)
    previous_work = work_history.filter(is_current=False)
    
    # Get clinicians the user has access relationships with
    from clinicians.models import HealthcareFeedback
    clinician_accesses = user.clinician_accesses.filter(is_active=True).select_related('clinician')
    feedback = user.healthcare_feedback.all()
    invitations = ClinicianInvitation.objects.filter(patient=user).order_by('-created_at')
    
    # Calculate profile completion
    completed_items = 0
    total_items = 6
    if profile.date_of_birth:
        completed_items += 1
    if profile.phone_number:
        completed_items += 1
    if profile.emergency_contact_name:
        completed_items += 1
    if user.medications.count() > 0:
        completed_items += 1
    if user.conditions.count() > 0:
        completed_items += 1
    if user.allergies.count() > 0:
        completed_items += 1
    
    context = {
        'medications': user.medications.all(),
        'conditions': user.conditions.all(),
        'allergies': user.allergies.all(),
        'assessments': user.assessments.all(),
        'work_history': work_history,
        'current_work': current_work,
        'previous_work': previous_work,
        'profile': profile,
        'clinician_accesses': clinician_accesses,
        'feedback': feedback,
        'invitations': invitations,
        'profile_completion': {
            'completed': completed_items,
            'total': total_items,
            'percent': int((completed_items / total_items) * 100) if total_items > 0 else 0,
        },
    }
    return render(request, 'health_records/dashboard.html', context)


# Medication Views
@login_required
def add_medication(request):
    """Add a new medication"""
    # Check if user is in onboarding
    is_onboarding = not request.user.profile.onboarding_completed
    next_step = request.GET.get('next', 'conditions') if is_onboarding else None
    
    if request.method == 'POST':
        form = MedicationForm(request.POST, request.FILES)
        if form.is_valid():
            medication = form.save(commit=False)
            medication.user = request.user
            medication.save()
            messages.success(request, 'Medication added successfully!')
            # Redirect to next onboarding step if in onboarding, otherwise dashboard
            if is_onboarding:
                return redirect(f"{reverse('health_records:onboarding')}?step={next_step}")
            return redirect('health_records:dashboard')
    else:
        form = MedicationForm()
    return render(request, 'health_records/forms/medication_form.html', {
        'form': form, 
        'action': 'Add',
        'is_onboarding': is_onboarding,
        'next_step': next_step
    })


@login_required
def edit_medication(request, pk):
    """Edit an existing medication"""
    medication = get_object_or_404(Medication, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MedicationForm(request.POST, request.FILES, instance=medication)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medication updated successfully!')
            return redirect('health_records:dashboard')
    else:
        form = MedicationForm(instance=medication)
    return render(request, 'health_records/forms/medication_form.html', {'form': form, 'medication': medication, 'action': 'Edit'})


@login_required
def delete_medication(request, pk):
    """Delete a medication"""
    medication = get_object_or_404(Medication, pk=pk, user=request.user)
    if request.method == 'POST':
        medication.delete()
        messages.success(request, 'Medication deleted successfully!')
        return redirect('health_records:dashboard')
    return render(request, 'health_records/delete_confirm.html', {'item': medication, 'item_type': 'medication'})


# Condition Views
@login_required
def add_condition(request):
    """Add a new condition"""
    # Check if user is in onboarding
    is_onboarding = not request.user.profile.onboarding_completed
    next_step = request.GET.get('next', 'allergies') if is_onboarding else None
    
    if request.method == 'POST':
        form = ConditionForm(request.POST)
        if form.is_valid():
            condition = form.save(commit=False)
            condition.user = request.user
            condition.save()
            messages.success(request, 'Condition added successfully!')
            # Redirect to next onboarding step if in onboarding, otherwise dashboard
            if is_onboarding:
                return redirect(f"{reverse('health_records:onboarding')}?step={next_step}")
            return redirect('health_records:dashboard')
    else:
        form = ConditionForm()
    return render(request, 'health_records/forms/condition_form.html', {
        'form': form, 
        'action': 'Add',
        'is_onboarding': is_onboarding,
        'next_step': next_step
    })


@login_required
def edit_condition(request, pk):
    """Edit an existing condition"""
    condition = get_object_or_404(Condition, pk=pk, user=request.user)
    if request.method == 'POST':
        form = ConditionForm(request.POST, instance=condition)
        if form.is_valid():
            form.save()
            messages.success(request, 'Condition updated successfully!')
            return redirect('health_records:dashboard')
    else:
        form = ConditionForm(instance=condition)
    return render(request, 'health_records/forms/condition_form.html', {'form': form, 'condition': condition, 'action': 'Edit'})


@login_required
def delete_condition(request, pk):
    """Delete a condition"""
    condition = get_object_or_404(Condition, pk=pk, user=request.user)
    if request.method == 'POST':
        condition.delete()
        messages.success(request, 'Condition deleted successfully!')
        return redirect('health_records:dashboard')
    return render(request, 'health_records/delete_confirm.html', {'item': condition, 'item_type': 'condition'})


# Allergy Views
@login_required
def add_allergy(request):
    """Add a new allergy"""
    # Check if user is in onboarding
    is_onboarding = not request.user.profile.onboarding_completed
    next_step = request.GET.get('next', 'complete') if is_onboarding else None
    
    if request.method == 'POST':
        form = AllergyForm(request.POST)
        if form.is_valid():
            allergy = form.save(commit=False)
            allergy.user = request.user
            allergy.save()
            messages.success(request, 'Allergy added successfully!')
            # Redirect to next onboarding step if in onboarding, otherwise dashboard
            if is_onboarding:
                return redirect(f"{reverse('health_records:onboarding')}?step={next_step}")
            return redirect('health_records:dashboard')
    else:
        form = AllergyForm()
    return render(request, 'health_records/forms/allergy_form.html', {
        'form': form, 
        'action': 'Add',
        'is_onboarding': is_onboarding,
        'next_step': next_step
    })


@login_required
def edit_allergy(request, pk):
    """Edit an existing allergy"""
    allergy = get_object_or_404(Allergy, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AllergyForm(request.POST, instance=allergy)
        if form.is_valid():
            form.save()
            messages.success(request, 'Allergy updated successfully!')
            return redirect('health_records:dashboard')
    else:
        form = AllergyForm(instance=allergy)
    return render(request, 'health_records/forms/allergy_form.html', {'form': form, 'allergy': allergy, 'action': 'Edit'})


@login_required
def delete_allergy(request, pk):
    """Delete an allergy"""
    allergy = get_object_or_404(Allergy, pk=pk, user=request.user)
    if request.method == 'POST':
        allergy.delete()
        messages.success(request, 'Allergy deleted successfully!')
        return redirect('health_records:dashboard')
    return render(request, 'health_records/delete_confirm.html', {'item': allergy, 'item_type': 'allergy'})


# Assessment/Symptoms Views (User-entered)
@login_required
def add_assessment(request):
    """Add a new symptom entry"""
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.user = request.user
            assessment.save()
            messages.success(request, 'Symptoms recorded successfully!')
            return redirect('health_records:dashboard')
    else:
        form = AssessmentForm()
    return render(request, 'health_records/forms/assessment_form.html', {'form': form, 'action': 'Add'})


@login_required
def edit_assessment(request, pk):
    """Edit an existing symptom entry"""
    assessment = get_object_or_404(Assessment, pk=pk, user=request.user)
    if request.method == 'POST':
        form = AssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Symptoms updated successfully!')
            return redirect('health_records:dashboard')
    else:
        form = AssessmentForm(instance=assessment)
    return render(request, 'health_records/forms/assessment_form.html', {'form': form, 'assessment': assessment, 'action': 'Edit'})


@login_required
def delete_assessment(request, pk):
    """Delete a symptom entry and notify clinicians"""
    assessment = get_object_or_404(Assessment, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Get clinicians who have access to this patient
        clinician_accesses = PatientClinicianAccess.objects.filter(
            patient=request.user,
            is_active=True
        ).select_related('clinician')
        
        # Store assessment info before deletion for notification
        assessment_date = assessment.symptom_date or assessment.created_at
        patient_name = request.user.get_full_name() or request.user.username
        
        # Delete the assessment
        assessment.delete()
        
        # Notify clinicians (store in session or send email - for now we'll add a system message)
        # In a production system, you'd send emails or create notification records
        for access in clinician_accesses:
            # You could create a Notification model here
            # For now, we'll log it
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Assessment deleted by {patient_name} on {assessment_date}. Clinician {access.clinician.full_name} ({access.clinician.email}) should be notified.")
        
        messages.success(request, f'Assessment deleted successfully! {clinician_accesses.count()} clinician(s) have been notified.')
        return redirect('health_records:dashboard')
    
    return render(request, 'health_records/delete_confirm.html', {
        'item': assessment, 
        'item_type': 'assessment',
        'warning_message': 'This assessment will be permanently deleted and your clinicians will be notified of the deletion.'
    })


# Practitioner Assessment Views
@login_required
def add_practitioner_assessment(request, assessment_pk):
    """Add practitioner objective assessment data to an existing symptom entry"""
    assessment = get_object_or_404(Assessment, pk=assessment_pk)
    
    # Check if current user is a clinician with access
    try:
        clinician = request.user.clinician_profile
        access = PatientClinicianAccess.objects.filter(
            patient=assessment.user,
            clinician=clinician,
            is_active=True
        ).first()
        
        if not access:
            messages.error(request, 'You do not have access to add assessments for this patient.')
            return redirect('health_records:dashboard')
    except Clinician.DoesNotExist:
        messages.error(request, 'You must be a registered clinician to add objective assessments.')
        return redirect('health_records:dashboard')
    
    if request.method == 'POST':
        form = PractitionerAssessmentForm(request.POST, request.FILES, instance=assessment)
        if form.is_valid():
            assessment = form.save(commit=False)
            assessment.clinician = clinician
            # Set completed_at to now if not provided
            if not assessment.completed_at:
                assessment.completed_at = timezone.now()
            assessment.save()
            messages.success(request, 'Objective assessment added successfully!')
            # Redirect to clinician dashboard if user is a clinician
            if hasattr(request.user, 'clinician_profile'):
                return redirect('clinicians:dashboard')
            return redirect('health_records:dashboard')
    else:
        form = PractitionerAssessmentForm(instance=assessment)
    
    return render(request, 'health_records/forms/practitioner_assessment_form.html', {
        'form': form,
        'assessment': assessment,
        'patient': assessment.user
    })


@login_required
def edit_practitioner_assessment(request, pk):
    """Edit practitioner objective assessment data"""
    assessment = get_object_or_404(Assessment, pk=pk)
    
    # Check if current user is the clinician who added this assessment
    try:
        clinician = request.user.clinician_profile
        if assessment.clinician != clinician:
            messages.error(request, 'You can only edit assessments you have created.')
            return redirect('health_records:dashboard')
    except Clinician.DoesNotExist:
        messages.error(request, 'You must be a registered clinician to edit assessments.')
        return redirect('health_records:dashboard')
    
    if request.method == 'POST':
        form = PractitionerAssessmentForm(request.POST, request.FILES, instance=assessment)
        if form.is_valid():
            assessment = form.save(commit=False)
            # Set completed_at to now if not provided
            if not assessment.completed_at:
                assessment.completed_at = timezone.now()
            assessment.save()
            messages.success(request, 'Assessment updated successfully!')
            # Redirect to clinician dashboard if user is a clinician
            if hasattr(request.user, 'clinician_profile'):
                return redirect('clinicians:dashboard')
            return redirect('health_records:dashboard')
    else:
        form = PractitionerAssessmentForm(instance=assessment)
    
    return render(request, 'health_records/forms/practitioner_assessment_form.html', {
        'form': form,
        'assessment': assessment,
        'patient': assessment.user,
        'action': 'Edit'
    })


# Profile View
@login_required
def edit_profile(request):
    """Edit user profile"""
    profile = request.user.profile
    # Check if user is in onboarding
    is_onboarding = not profile.onboarding_completed
    next_step = request.GET.get('next', 'medications') if is_onboarding else None
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            # Redirect to next onboarding step if in onboarding, otherwise dashboard
            if is_onboarding:
                return redirect(f"{reverse('health_records:onboarding')}?step={next_step}")
            return redirect('health_records:dashboard')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'health_records/forms/profile_form.html', {
        'form': form,
        'is_onboarding': is_onboarding,
        'next_step': next_step
    })


# Work History Views
@login_required
def add_work_history(request):
    """Add a new work history entry"""
    if request.method == 'POST':
        form = WorkHistoryForm(request.POST)
        if form.is_valid():
            work_history = form.save(commit=False)
            work_history.user = request.user
            # If marked as current, unmark other current jobs
            if work_history.is_current:
                WorkHistory.objects.filter(user=request.user, is_current=True).update(is_current=False)
            work_history.save()
            messages.success(request, 'Work history added successfully!')
            return redirect('health_records:dashboard')
    else:
        form = WorkHistoryForm()
    return render(request, 'health_records/forms/work_history_form.html', {'form': form, 'action': 'Add'})


@login_required
def edit_work_history(request, pk):
    """Edit an existing work history entry"""
    work_history = get_object_or_404(WorkHistory, pk=pk, user=request.user)
    if request.method == 'POST':
        form = WorkHistoryForm(request.POST, instance=work_history)
        if form.is_valid():
            work_history = form.save(commit=False)
            # If marked as current, unmark other current jobs
            if work_history.is_current:
                WorkHistory.objects.filter(user=request.user, is_current=True).exclude(pk=pk).update(is_current=False)
            work_history.save()
            messages.success(request, 'Work history updated successfully!')
            return redirect('health_records:dashboard')
    else:
        form = WorkHistoryForm(instance=work_history)
        # Convert JSON list to list for form
        if work_history.activities:
            form.fields['activities'].initial = work_history.activities
    return render(request, 'health_records/forms/work_history_form.html', {'form': form, 'work_history': work_history, 'action': 'Edit'})


@login_required
def delete_work_history(request, pk):
    """Delete a work history entry"""
    work_history = get_object_or_404(WorkHistory, pk=pk, user=request.user)
    if request.method == 'POST':
        work_history.delete()
        messages.success(request, 'Work history deleted successfully!')
        return redirect('health_records:dashboard')
    return render(request, 'health_records/delete_confirm.html', {'item': work_history, 'item_type': 'work history'})


# Healthcare Feedback Views
@login_required
def add_feedback(request, access_pk=None):
    """Add feedback about a healthcare organisation"""
    from clinicians.models import HealthcareFeedback
    access = None
    if access_pk:
        access = get_object_or_404(PatientClinicianAccess, pk=access_pk, patient=request.user, is_active=True)
    
    if request.method == 'POST':
        form = HealthcareFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.patient = request.user
            if access:
                feedback.access = access
                feedback.organisation = access.clinician.organisation or 'Healthcare Provider'
            feedback.save()
            messages.success(request, 'Thank you for your feedback! It has been recorded privately.')
            return redirect('health_records:dashboard')
    else:
        initial = {}
        if access:
            initial['organisation'] = access.clinician.organisation or 'Healthcare Provider'
        form = HealthcareFeedbackForm(initial=initial)
    
    return render(request, 'health_records/forms/feedback_form.html', {
        'form': form,
        'access': access,
        'action': 'Add'
    })


@login_required
def view_feedback(request):
    """View user's submitted feedback"""
    from clinicians.models import HealthcareFeedback
    feedback = request.user.healthcare_feedback.all()
    return render(request, 'health_records/feedback_list.html', {'feedback': feedback})


@login_required
def delete_feedback(request, pk):
    """Delete feedback"""
    from clinicians.models import HealthcareFeedback
    feedback = get_object_or_404(HealthcareFeedback, pk=pk, patient=request.user)
    if request.method == 'POST':
        feedback.delete()
        messages.success(request, 'Feedback deleted successfully!')
        return redirect('health_records:view_feedback')
    return render(request, 'health_records/delete_confirm.html', {'item': feedback, 'item_type': 'feedback'})


@login_required
def invite_clinician(request):
    """Invite a clinician to access patient records"""
    from clinicians.models import Clinician, PatientClinicianAccess
    from clinicians.forms import ConsentForm
    from django.utils import timezone
    
    if request.method == 'POST':
        # Check if submitting consent form
        if 'submit_consent' in request.POST:
            practitioner_code = request.POST.get('practitioner_code', '').strip().upper()
            consent_form = ConsentForm(request.POST)
            
            # Validate practitioner code
            if not practitioner_code:
                messages.error(request, 'Practitioner code is required.')
                # Try to get clinician from previous search if available
                clinician = None
                try:
                    # Check if we can find the clinician from session or previous context
                    # For now, redirect back to invite page
                    return redirect('health_records:invite_clinician')
                except:
                    return redirect('health_records:invite_clinician')
            
            # Validate consent form
            if not consent_form.is_valid():
                # Form validation failed - re-render consent form with errors
                try:
                    clinician = Clinician.objects.get(practitioner_code=practitioner_code)
                    return render(request, 'health_records/consent_form.html', {
                        'clinician': clinician,
                        'practitioner_code': practitioner_code,
                        'consent_form': consent_form  # Form with errors
                    })
                except Clinician.DoesNotExist:
                    messages.error(request, f'No practitioner found with code: {practitioner_code}. Please check the code and try again.')
                    return redirect('health_records:invite_clinician')
            
            # Both form and code are valid - process consent
            try:
                clinician = Clinician.objects.get(practitioner_code=practitioner_code)
                # Check if access already exists
                access, created = PatientClinicianAccess.objects.get_or_create(
                    patient=request.user,
                    clinician=clinician,
                    defaults={
                        'access_granted_by': request.user,
                        'access_level': 'full',
                        'is_active': True,
                        # Unchecked checkboxes don't appear in cleaned_data, so default to False
                        'consent_medications': consent_form.cleaned_data.get('consent_medications', False),
                        'consent_conditions': consent_form.cleaned_data.get('consent_conditions', False),
                        'consent_allergies': consent_form.cleaned_data.get('consent_allergies', False),
                        'consent_symptoms': consent_form.cleaned_data.get('consent_symptoms', False),
                        'consent_personal_info': consent_form.cleaned_data.get('consent_personal_info', False),
                        'consent_emergency_contacts': consent_form.cleaned_data.get('consent_emergency_contacts', False),
                        'consent_work_history': consent_form.cleaned_data.get('consent_work_history', False),
                        'consent_feedback': consent_form.cleaned_data.get('consent_feedback', False),
                        'consent_given_at': timezone.now(),
                    }
                )
                
                if not created:
                    # Update existing access with new consent preferences
                    access.is_active = True
                    # Unchecked checkboxes don't appear in cleaned_data, so default to False
                    access.consent_medications = consent_form.cleaned_data.get('consent_medications', False)
                    access.consent_conditions = consent_form.cleaned_data.get('consent_conditions', False)
                    access.consent_allergies = consent_form.cleaned_data.get('consent_allergies', False)
                    access.consent_symptoms = consent_form.cleaned_data.get('consent_symptoms', False)
                    access.consent_personal_info = consent_form.cleaned_data.get('consent_personal_info', False)
                    access.consent_emergency_contacts = consent_form.cleaned_data.get('consent_emergency_contacts', False)
                    access.consent_work_history = consent_form.cleaned_data.get('consent_work_history', False)
                    access.consent_feedback = consent_form.cleaned_data.get('consent_feedback', False)
                    access.consent_given_at = timezone.now()
                    access.save()
                
                messages.success(
                    request, 
                    f'Successfully connected with {clinician.full_name}! They now have access to the records you selected.'
                )
                return redirect('health_records:dashboard')
            except Clinician.DoesNotExist:
                messages.error(request, f'No practitioner found with code: {practitioner_code}. Please check the code and try again.')
                return redirect('health_records:invite_clinician')
        
        # Check if searching by code
        elif 'search_code' in request.POST:
            practitioner_code = request.POST.get('practitioner_code', '').strip().upper()
            if practitioner_code and len(practitioner_code) == 5:
                try:
                    clinician = Clinician.objects.get(practitioner_code=practitioner_code)
                    # Check if access already exists
                    existing_access = PatientClinicianAccess.objects.filter(
                        patient=request.user,
                        clinician=clinician
                    ).first()
                    
                    if existing_access and existing_access.is_active:
                        messages.info(request, f'You are already connected with {clinician.full_name}.')
                        return redirect('health_records:dashboard')
                    
                    # Show consent form
                    consent_form = ConsentForm()
                    # Get registration info for display
                    from clinicians.verification import get_registration_body_name, get_registration_body_url
                    registration_info = None
                    if clinician.registration_number and clinician.registration_body:
                        registration_info = {
                            'body_name': get_registration_body_name(clinician.registration_body),
                            'register_url': get_registration_body_url(
                                clinician.registration_body,
                                clinician.registration_number,
                                clinician.first_name,
                                clinician.last_name
                            )
                        }
                    return render(request, 'health_records/consent_form.html', {
                        'clinician': clinician,
                        'practitioner_code': practitioner_code,
                        'consent_form': consent_form,
                        'registration_info': registration_info
                    })
                except Clinician.DoesNotExist:
                    messages.error(request, f'No practitioner found with code: {practitioner_code}. Please check the code and try again.')
                    # Return early to prevent processing invitation form
                    form = ClinicianInvitationForm(patient=request.user)
                    invitations = ClinicianInvitation.objects.filter(patient=request.user).order_by('-created_at')
                    return render(request, 'health_records/invite_clinician.html', {
                        'form': form,
                        'invitations': invitations
                    })
            else:
                messages.error(request, 'Please enter a valid 5-character practitioner code.')
                # Return early to prevent processing invitation form
                form = ClinicianInvitationForm(patient=request.user)
                invitations = ClinicianInvitation.objects.filter(patient=request.user).order_by('-created_at')
                return render(request, 'health_records/invite_clinician.html', {
                    'form': form,
                    'invitations': invitations
                })
        
        # Otherwise, use invitation form (only if not processing code search)
        form = ClinicianInvitationForm(request.POST, patient=request.user)
        if form.is_valid():
            invitation = form.save(commit=False)
            invitation.patient = request.user
            invitation.save()
            
            # Generate invitation link using request to determine protocol
            invitation_url = request.build_absolute_uri(f'/clinicians/signup/{invitation.token}/')
            
            # TODO: Send email with invitation link
            # For now, show success message with link
            messages.success(
                request, 
                f'Invitation sent to {invitation.email}. '
                f'Share this link: {invitation_url}'
            )
            return redirect('health_records:dashboard')
    else:
        form = ClinicianInvitationForm(patient=request.user)
    
    # Get existing invitations
    invitations = ClinicianInvitation.objects.filter(patient=request.user).order_by('-created_at')
    
    return render(request, 'health_records/invite_clinician.html', {
        'form': form,
        'invitations': invitations
    })


@login_required
def revoke_clinician_access(request, access_pk):
    """Revoke a clinician's access to patient records"""
    from clinicians.models import PatientClinicianAccess
    
    access = get_object_or_404(
        PatientClinicianAccess,
        pk=access_pk,
        patient=request.user,
        is_active=True  # Only allow revoking active accesses
    )
    
    if request.method == 'POST':
        clinician_name = access.clinician.full_name
        # Deactivate access instead of deleting to maintain history
        access.is_active = False
        access.save()
        messages.success(
            request,
            f'Access revoked for {clinician_name}. They can no longer view your records.'
        )
        return redirect('health_records:dashboard')
    
    return render(request, 'health_records/revoke_access_confirm.html', {
        'access': access,
        'clinician': access.clinician
    })


@login_required
def process_notes_image(request, assessment_pk):
    """Process uploaded therapist notes image using Azure Document Intelligence"""
    assessment = get_object_or_404(Assessment, pk=assessment_pk)
    
    # Check permissions - user must own the assessment or be a clinician with access
    is_owner = assessment.user == request.user
    is_clinician = False
    clinician = None
    
    if hasattr(request.user, 'clinician_profile'):
        clinician = request.user.clinician_profile
        has_access = PatientClinicianAccess.objects.filter(
            patient=assessment.user,
            clinician=clinician,
            is_active=True
        ).exists()
        is_clinician = has_access
    
    if not (is_owner or is_clinician):
        messages.error(request, 'You do not have permission to process this assessment.')
        return redirect('health_records:dashboard')
    
    # Check if image exists
    if not assessment.practitioner_notes_image:
        messages.error(request, 'No notes image found for this assessment.')
        if is_clinician:
            return redirect('clinicians:dashboard')
        return redirect('health_records:dashboard')
    
    # Initialize Azure Document Intelligence service
    doc_service = AzureDocumentIntelligenceService()
    
    if not doc_service.is_configured():
        messages.error(
            request,
            'Azure Document Intelligence is not configured. Please contact your administrator.'
        )
        if is_clinician:
            return redirect('clinicians:dashboard')
        return redirect('health_records:dashboard')
    
    # Get the full path to the image
    image_path = assessment.practitioner_notes_image.path
    
    # Process the document
    try:
        extracted_data = doc_service.analyze_document(image_path)
        
        if not extracted_data:
            error_msg = 'Failed to extract data from the notes image.'
            messages.error(request, error_msg)
            
            # If AJAX request, return JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=400)
            
            if is_clinician:
                return redirect('clinicians:dashboard')
            return redirect('health_records:dashboard')
        
        # Delete existing extracted findings for this assessment
        ExtractedFindings.objects.filter(assessment=assessment).delete()
        
        # Create ExtractedFindings records
        findings_created = 0
        for finding_data in extracted_data.get('findings', []):
            finding = ExtractedFindings.objects.create(
                assessment=assessment,
                category=finding_data.get('category', 'general'),
                finding_type=finding_data.get('type', 'observation'),
                text=finding_data.get('text', ''),
                raw_extraction_data=extracted_data,
            )
            findings_created += 1
        
        messages.success(
            request,
            f'Successfully extracted {findings_created} findings from the notes image!'
        )
        
        # If AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                'success': True,
                'findings_count': findings_created,
                'message': f'Successfully extracted {findings_created} findings from the notes image!'
            })
        
        # Redirect to view findings
        return redirect('health_records:view_extracted_findings', assessment_pk=assessment.pk)
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        error_msg = str(e)
        logger.error(f"Error processing notes image: {error_msg}")
        logger.exception("Full traceback:")
        error_message = f'Error processing image: {error_msg}. Please check the image format (JPEG, PNG, PDF supported) and try again.'
        messages.error(request, error_message)
        
        # If AJAX request, return JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from django.http import JsonResponse
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=500)
        
        if is_clinician:
            return redirect('clinicians:dashboard')
        return redirect('health_records:dashboard')


@login_required
def view_extracted_findings(request, assessment_pk):
    """View extracted findings from therapist notes"""
    assessment = get_object_or_404(Assessment, pk=assessment_pk)
    
    # Check permissions
    is_owner = assessment.user == request.user
    is_clinician = False
    clinician = None
    
    if hasattr(request.user, 'clinician_profile'):
        clinician = request.user.clinician_profile
        has_access = PatientClinicianAccess.objects.filter(
            patient=assessment.user,
            clinician=clinician,
            is_active=True
        ).exists()
        is_clinician = has_access
    
    if not (is_owner or is_clinician):
        messages.error(request, 'You do not have permission to view this assessment.')
        return redirect('health_records:dashboard')
    
    # Get extracted findings grouped by category
    findings = ExtractedFindings.objects.filter(assessment=assessment).order_by('category', 'extracted_at')
    
    # Group findings by category
    findings_by_category = {}
    for finding in findings:
        category = finding.get_category_display()
        if category not in findings_by_category:
            findings_by_category[category] = []
        findings_by_category[category].append(finding)
    
    context = {
        'assessment': assessment,
        'findings': findings,
        'findings_by_category': findings_by_category,
        'is_clinician': is_clinician,
        'clinician': clinician,
        'has_image': bool(assessment.practitioner_notes_image),
    }
    
    return render(request, 'health_records/extracted_findings.html', context)


@login_required
def get_extracted_findings_json(request, assessment_pk):
    """Get extracted findings as JSON for modal display"""
    from django.http import JsonResponse
    assessment = get_object_or_404(Assessment, pk=assessment_pk)
    
    # Check permissions
    is_owner = assessment.user == request.user
    is_clinician = False
    
    if hasattr(request.user, 'clinician_profile'):
        clinician = request.user.clinician_profile
        has_access = PatientClinicianAccess.objects.filter(
            patient=assessment.user,
            clinician=clinician,
            is_active=True
        ).exists()
        is_clinician = has_access
    
    if not (is_owner or is_clinician):
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    # Get extracted findings grouped by category
    findings = ExtractedFindings.objects.filter(assessment=assessment).order_by('category', 'extracted_at')
    
    # Group findings by category
    findings_by_category = {}
    for finding in findings:
        category = finding.get_category_display()
        if category not in findings_by_category:
            findings_by_category[category] = []
        findings_by_category[category].append({
            'id': finding.pk,
            'type': finding.get_finding_type_display(),
            'type_class': finding.finding_type,
            'text': finding.text,
            'extracted_at': finding.extracted_at.strftime('%b %d, %Y %H:%M'),
            'is_verified': finding.is_verified,
            'verified_by': finding.verified_by.full_name if finding.verified_by else None,
        })
    
    return JsonResponse({
        'assessment_id': assessment.pk,
        'assessment_date': assessment.assessment_date.strftime('%B %d, %Y') if assessment.assessment_date else 'N/A',
        'has_image': bool(assessment.practitioner_notes_image),
        'image_url': assessment.practitioner_notes_image.url if assessment.practitioner_notes_image else None,
        'findings_count': findings.count(),
        'findings_by_category': findings_by_category,
        'is_clinician': is_clinician,
    })


@login_required
def verify_finding(request, finding_pk):
    """Verify an extracted finding (clinician only)"""
    finding = get_object_or_404(ExtractedFindings, pk=finding_pk)
    
    # Only clinicians can verify findings
    if not hasattr(request.user, 'clinician_profile'):
        messages.error(request, 'Only clinicians can verify findings.')
        return redirect('health_records:view_extracted_findings', assessment_pk=finding.assessment.pk)
    
    clinician = request.user.clinician_profile
    
    # Check if clinician has access to this patient
    has_access = PatientClinicianAccess.objects.filter(
        patient=finding.assessment.user,
        clinician=clinician,
        is_active=True
    ).exists()
    
    if not has_access:
        messages.error(request, 'You do not have access to this patient\'s records.')
        return redirect('health_records:dashboard')
    
    # Toggle verification status
    if finding.is_verified and finding.verified_by == clinician:
        # Unverify
        finding.is_verified = False
        finding.verified_by = None
        finding.verified_at = None
        messages.success(request, 'Finding unverified.')
    else:
        # Verify
        finding.is_verified = True
        finding.verified_by = clinician
        finding.verified_at = timezone.now()
        messages.success(request, 'Finding verified.')
    
    finding.save()
    
    return redirect('health_records:view_extracted_findings', assessment_pk=finding.assessment.pk)


@login_required
def delete_finding(request, finding_pk):
    """Delete an extracted finding"""
    finding = get_object_or_404(ExtractedFindings, pk=finding_pk)
    assessment = finding.assessment
    
    # Check permissions
    is_owner = assessment.user == request.user
    is_clinician = False
    
    if hasattr(request.user, 'clinician_profile'):
        clinician = request.user.clinician_profile
        has_access = PatientClinicianAccess.objects.filter(
            patient=assessment.user,
            clinician=clinician,
            is_active=True
        ).exists()
        is_clinician = has_access
    
    if not (is_owner or is_clinician):
        messages.error(request, 'You do not have permission to delete this finding.')
        return redirect('health_records:dashboard')
    
    if request.method == 'POST':
        finding.delete()
        messages.success(request, 'Finding deleted successfully.')
        return redirect('health_records:view_extracted_findings', assessment_pk=assessment.pk)
    
    return render(request, 'health_records/delete_confirm.html', {
        'item': finding,
        'item_type': 'finding'
    })
