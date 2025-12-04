from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Medication, Condition, Allergy, Assessment, WorkHistory
from accounts.models import UserProfile
from .forms import (
    MedicationForm, ConditionForm, AllergyForm, 
    AssessmentForm, PractitionerAssessmentForm, UserProfileForm, WorkHistoryForm
)
from clinicians.models import PatientClinicianAccess, Clinician, ClinicianInvitation
from clinicians.forms import HealthcareFeedbackForm, ClinicianInvitationForm


def home(request):
    """Homepage view"""
    return render(request, 'health_records/home.html')


@login_required
def dashboard(request):
    """User dashboard view"""
    user = request.user
    work_history = user.work_history.all()
    current_work = work_history.filter(is_current=True)
    previous_work = work_history.filter(is_current=False)
    
    # Get clinicians the user has access relationships with
    from clinicians.models import HealthcareFeedback
    clinician_accesses = user.clinician_accesses.filter(is_active=True).select_related('clinician')
    feedback = user.healthcare_feedback.all()
    invitations = ClinicianInvitation.objects.filter(patient=user).order_by('-created_at')
    
    context = {
        'medications': user.medications.all(),
        'conditions': user.conditions.all(),
        'allergies': user.allergies.all(),
        'assessments': user.assessments.all(),
        'work_history': work_history,
        'current_work': current_work,
        'previous_work': previous_work,
        'profile': user.profile,
        'clinician_accesses': clinician_accesses,
        'feedback': feedback,
        'invitations': invitations,
    }
    return render(request, 'health_records/dashboard.html', context)


# Medication Views
@login_required
def add_medication(request):
    """Add a new medication"""
    if request.method == 'POST':
        form = MedicationForm(request.POST, request.FILES)
        if form.is_valid():
            medication = form.save(commit=False)
            medication.user = request.user
            medication.save()
            messages.success(request, 'Medication added successfully!')
            return redirect('health_records:dashboard')
    else:
        form = MedicationForm()
    return render(request, 'health_records/forms/medication_form.html', {'form': form, 'action': 'Add'})


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
    if request.method == 'POST':
        form = ConditionForm(request.POST)
        if form.is_valid():
            condition = form.save(commit=False)
            condition.user = request.user
            condition.save()
            messages.success(request, 'Condition added successfully!')
            return redirect('health_records:dashboard')
    else:
        form = ConditionForm()
    return render(request, 'health_records/forms/condition_form.html', {'form': form, 'action': 'Add'})


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
    if request.method == 'POST':
        form = AllergyForm(request.POST)
        if form.is_valid():
            allergy = form.save(commit=False)
            allergy.user = request.user
            allergy.save()
            messages.success(request, 'Allergy added successfully!')
            return redirect('health_records:dashboard')
    else:
        form = AllergyForm()
    return render(request, 'health_records/forms/allergy_form.html', {'form': form, 'action': 'Add'})


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
    """Delete a symptom entry"""
    assessment = get_object_or_404(Assessment, pk=pk, user=request.user)
    if request.method == 'POST':
        assessment.delete()
        messages.success(request, 'Symptom entry deleted successfully!')
        return redirect('health_records:dashboard')
    return render(request, 'health_records/delete_confirm.html', {'item': assessment, 'item_type': 'symptom entry'})


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
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('health_records:dashboard')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'health_records/forms/profile_form.html', {'form': form})


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
    """Add feedback about a healthcare organization"""
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
                    return render(request, 'health_records/consent_form.html', {
                        'clinician': clinician,
                        'practitioner_code': practitioner_code,
                        'consent_form': consent_form
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
